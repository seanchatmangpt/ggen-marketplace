"""Temprun fuel <-> valve composition courts (fuel-refusal binding).

The strata-temprun-pack ontology declares that arena fuel exhaustion emits
a valve-taxonomy refusal: the strata-valve-pack's
valve:FuelExhaustedRefusal class, cited by pinned IRI literal (no
owl:imports, house style) with the valve's 32-byte receipt wire constant.
Composition law and receipts: packs/strata-temprun-pack/ontology.ttl,
gates/020_fuel_refusal_binding.rq, generated/fuel_refusal_binding.rs.

Chicago style: real ggen subprocess syncs in tmp copies, real rdflib over
the pack ontologies, no mocks. Skips carry a "BLOCKED:" reason prefix when
ggen is unavailable.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, cast

import pytest
from rdflib import Graph, URIRef

ROOT = Path(__file__).resolve().parents[1]
TEMPRUN = ROOT / "packs" / "strata-temprun-pack"
VALVE = ROOT / "packs" / "strata-valve-pack"

ST = "https://strata.chatman.ai/ontology#"
VALVE_NS = "https://strata.chatman.ai/ontology/valve#"
FUEL_EXHAUSTED_IRI = VALVE_NS + "FuelExhaustedRefusal"
RECEIPT_LEN = 32

EXPECTED_IRI_CONST = (
    'pub const FUEL_EXHAUSTED_REFUSAL_IRI: &str = "%s";' % FUEL_EXHAUSTED_IRI
)
EXPECTED_RECEIPT_CONST = "pub const REFUSAL_RECEIPT_LEN: usize = 32"


def _ggen_binary() -> str | None:
    return os.environ.get("GGEN_BIN") or shutil.which("ggen")


def _copy_pack(dest: Path) -> Path:
    shutil.copytree(TEMPRUN, dest / "pack")
    return dest / "pack"


def _run_sync(pack_dir: Path) -> subprocess.CompletedProcess:
    binary = _ggen_binary()
    if binary is None:
        pytest.skip("BLOCKED: ggen binary not on PATH")
    return subprocess.run(
        [binary, "sync", "run"], cwd=pack_dir, capture_output=True, text=True, timeout=300
    )


def _query_rows(graph: Graph, query: str) -> list[tuple]:
    return list(cast(Iterable[tuple], graph.query(query)))


# ---------------------------------------------------------------------------
# Court 1 — positive witness: honest sync exits 0 and the generated
# composition module carries the pinned IRI + receipt constant.
# ---------------------------------------------------------------------------
def test_positive_witness_sync_and_generated_content(tmp_path):
    dest = tmp_path / "pos"
    dest.mkdir()
    pack = _copy_pack(dest)
    proc = _run_sync(pack)
    assert proc.returncode == 0, f"sync refused: {proc.stdout}\n{proc.stderr}"
    out = pack / "generated" / "fuel_refusal_binding.rs"
    assert out.is_file(), "generated/fuel_refusal_binding.rs missing after honest sync"
    text = out.read_text(encoding="utf-8")
    assert EXPECTED_IRI_CONST in text, "pinned valve IRI constant missing/mutated"
    assert EXPECTED_RECEIPT_CONST in text, "32-byte receipt constant missing/mutated"
    assert "COMPOSITION LAW" in text, "composition-law doc comment missing"
    assert "Strata.Valve.Refusals.FuelExhausted" in text, (
        "valve module citation missing from the composition-law doc comment"
    )


# ---------------------------------------------------------------------------
# Court 2 — sync determinism: two honest syncs in separate tmp copies render
# generated/fuel_refusal_binding.rs byte-identically.
# ---------------------------------------------------------------------------
def test_sync_determinism_two_copies_byte_identical(tmp_path):
    dest1 = tmp_path / "det1"
    dest2 = tmp_path / "det2"
    dest1.mkdir()
    dest2.mkdir()
    bytes_runs = []
    for dest in (dest1, dest2):
        pack = _copy_pack(dest)
        proc = _run_sync(pack)
        assert proc.returncode == 0, f"sync refused: {proc.stdout}\n{proc.stderr}"
        out = pack / "generated" / "fuel_refusal_binding.rs"
        assert out.is_file()
        bytes_runs.append(out.read_bytes())
    assert bytes_runs[0] == bytes_runs[1], (
        "two honest syncs rendered different bytes — sync is not deterministic"
    )


# ---------------------------------------------------------------------------
# Court 3 — drift guard: the committed generated file matches a fresh honest
# render byte-for-byte (hand-edit / stale-projection detection).
# ---------------------------------------------------------------------------
def test_committed_generated_matches_fresh_render(tmp_path):
    dest = tmp_path / "drift"
    dest.mkdir()
    pack = _copy_pack(dest)
    proc = _run_sync(pack)
    assert proc.returncode == 0
    fresh = (pack / "generated" / "fuel_refusal_binding.rs").read_bytes()
    committed = (TEMPRUN / "generated" / "fuel_refusal_binding.rs").read_bytes()
    assert fresh == committed, (
        "committed generated/fuel_refusal_binding.rs drifted from a fresh sync render"
    )


# ---------------------------------------------------------------------------
# Court 4 — negative witness: corrupting the pinned valve IRI in the temprun
# ontology makes the fail-closed gate refuse the sync (nonzero exit).
# ---------------------------------------------------------------------------
def test_negative_witness_corrupted_iri_refused(tmp_path):
    dest = tmp_path / "neg"
    dest.mkdir()
    pack = _copy_pack(dest)
    ontology = pack / "ontology.ttl"
    text = ontology.read_text(encoding="utf-8")
    corrupted = text.replace(FUEL_EXHAUSTED_IRI, FUEL_EXHAUSTED_IRI + "X", 1)
    assert corrupted != text, "sabotage did not mutate the ontology"
    ontology.write_text(corrupted, encoding="utf-8")
    proc = _run_sync(pack)
    assert proc.returncode != 0, (
        "corrupted valve IRI was admitted — gate is vacuous"
    )
    assert "020_fuel_refusal_binding" in (proc.stdout + proc.stderr), (
        "refusal did not name the fuel-refusal-binding gate"
    )


# ---------------------------------------------------------------------------
# Court 5 — negative witness twin: corrupting the receipt length instead
# (different sabotage channel) must also be refused by the same gate.
# ---------------------------------------------------------------------------
def test_negative_witness_receipt_len_corruption_refused(tmp_path):
    dest = tmp_path / "neglen"
    dest.mkdir()
    pack = _copy_pack(dest)
    ontology = pack / "ontology.ttl"
    text = ontology.read_text(encoding="utf-8")
    corrupted = text.replace("st:refusalReceiptLen 32", "st:refusalReceiptLen 31", 1)
    assert corrupted != text, "sabotage did not mutate the ontology"
    ontology.write_text(corrupted, encoding="utf-8")
    proc = _run_sync(pack)
    assert proc.returncode != 0, "corrupted receipt length was admitted — gate is vacuous"


# ---------------------------------------------------------------------------
# Court 6 — sabotage twin (gate vacuity): corrupt the pinned IRI
# consistently (binding AND arena emission agree on the wrong IRI, so the
# unemitted_binding branch cannot fire), then delete the gate's
# wrong_refusal_class branch. The weakened gate must ADMIT that ontology —
# proving the real gate's refusal comes from that branch, not from sync
# failing for unrelated reasons.
# ---------------------------------------------------------------------------
GATE_020 = (TEMPRUN / "gates" / "020_fuel_refusal_binding.rq").read_text(
    encoding="utf-8"
)


def _gate_without_wrong_class_branch() -> str:
    marker = "  } UNION {\n    # The binding must pin exactly the valve FuelExhausted refusal class."
    start = GATE_020.index(marker) + len("  } UNION {\n")
    end = GATE_020.index("  } UNION {", start)
    weakened = GATE_020[:start] + GATE_020[end:]
    # Collapse the now-empty UNION branch the surgery leaves behind
    # ("} UNION {\n  } UNION {") — an empty group matches everything and
    # would itself produce a violation row in the engine.
    return weakened.replace("  } UNION {\n  } UNION {", "  } UNION {", 1)


def test_sabotage_twin_weakened_gate_admits_corrupted_iri(tmp_path):
    dest = tmp_path / "twin"
    dest.mkdir()
    pack = _copy_pack(dest)
    ontology = pack / "ontology.ttl"
    text = ontology.read_text(encoding="utf-8")
    ontology.write_text(
        # Consistent corruption: every occurrence moves to ...X so the
        # binding and the arena emission agree (unemitted_binding silent).
        text.replace(FUEL_EXHAUSTED_IRI, FUEL_EXHAUSTED_IRI + "X"),
        encoding="utf-8",
    )
    gate = pack / "gates" / "020_fuel_refusal_binding.rq"
    weakened = _gate_without_wrong_class_branch()
    assert weakened != GATE_020, "twin surgery did not mutate the gate"
    gate.write_text(weakened, encoding="utf-8")
    # ggen.toml closure hash? ggen sync re-reads the gate file directly.
    proc = _run_sync(pack)
    assert proc.returncode == 0, (
        "weakened gate still refused — refusal may come from another branch "
        f"(twin not discriminating): {proc.stdout}\n{proc.stderr}"
    )


# ---------------------------------------------------------------------------
# Court 7 — cross-pack identity: the pinned IRI in the temprun graph resolves
# to a real valve:RefusalClass in the valve graph (real rdflib, both packs).
# ---------------------------------------------------------------------------
def test_pinned_iri_is_declared_refusal_class_in_valve_graph():
    temprun = Graph()
    temprun.parse(TEMPRUN / "ontology.ttl", format="turtle")
    valve = Graph()
    valve.parse(VALVE / "ontology.ttl", format="turtle")

    # Pinned IRI present as a string literal in temprun (both the binding
    # and the arena emission).
    iris = {
        str(o)
        for s, p, o in temprun
        if str(o) == FUEL_EXHAUSTED_IRI
    }
    assert FUEL_EXHAUSTED_IRI in iris, "pinned valve IRI missing from temprun graph"

    # Emission edge: DefaultArena emits the pinned IRI.
    rows = _query_rows(
        temprun,
        f"""
        PREFIX st: <{ST}>
        SELECT ?iri WHERE {{
          ?a a st:ActuationArena ; st:emitsValveRefusal ?iri .
          FILTER(STR(?iri) = "{FUEL_EXHAUSTED_IRI}")
        }}""",
    )
    assert rows, "DefaultArena does not emit the pinned refusal IRI"

    # Cross-pack: the IRI is declared a valve:RefusalClass in the valve graph.
    cls = URIRef(FUEL_EXHAUSTED_IRI)
    assert (cls, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            URIRef(VALVE_NS + "RefusalClass")) in valve, (
        "pinned IRI is not a valve:RefusalClass in the valve graph"
    )
    atoms = [str(o) for o in valve.objects(cls, URIRef(VALVE_NS + "atom"))]
    assert atoms == ["fuel_exhausted"], atoms
