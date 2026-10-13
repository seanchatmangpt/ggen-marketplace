"""Stratus witness-valve <-> valve-taxonomy composition courts.

The strata-stratus-pack ontology binds its witness-valve layer to the
strata-valve-pack refusal taxonomy: every stratus valve declaration must
reference a valve-taxonomy refusal class IRI (the four Strata.Valve.Refusals
child-module atoms are pinned), and register/valve pairing must be closed
(every st:guardedBy edge resolves to a valve carrying a refusal emission
edge). The taxonomy constants are pinned by IRI literal (no owl:imports,
house style). Composition law and receipts:
packs/strata-stratus-pack/ontology.ttl, gates/020_valve_taxonomy_binding.rq,
generated/valve_taxonomy.rs.

Third cross-pack composition in the strata family, after temprun<->valve
(8b888e884) and net<->protocol (27ebb78c4) — same proven pattern.

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
STRATUS = ROOT / "packs" / "strata-stratus-pack"
VALVE = ROOT / "packs" / "strata-valve-pack"

ST = "https://strata.chatman.ai/ontology#"
VALVE_NS = "https://strata.chatman.ai/ontology/valve#"
FUEL_EXHAUSTED_IRI = VALVE_NS + "FuelExhaustedRefusal"
GATE = "020_valve_taxonomy_binding"

# (pinned IRI, atom, Strata.Valve.Refusals child module) — mirrored from
# strata-valve-pack ontology.ttl valve:RefusalClass individuals.
PINNED = (
    (VALVE_NS + "MalformedFrameRefusal", "malformed_frame",
     "Strata.Valve.Refusals.MalformedFrame"),
    (FUEL_EXHAUSTED_IRI, "fuel_exhausted",
     "Strata.Valve.Refusals.FuelExhausted"),
    (VALVE_NS + "ParentDiscontinuityRefusal", "parent_discontinuity",
     "Strata.Valve.Refusals.ParentDiscontinuity"),
    (VALVE_NS + "ArenaFailureRefusal", "arena_failure",
     "Strata.Valve.Refusals.ArenaFailure"),
)

RDF_TYPE = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
REFUSAL_CLASS = URIRef(VALVE_NS + "RefusalClass")
ATOM = URIRef(VALVE_NS + "atom")
MODULE = URIRef(VALVE_NS + "module")
EMITS = URIRef(ST + "emitsRefusalClass")
GUARDED_BY = URIRef(ST + "guardedBy")


def _ggen_binary() -> str | None:
    return os.environ.get("GGEN_BIN") or shutil.which("ggen")


def _copy_pack(dest: Path) -> Path:
    shutil.copytree(STRATUS, dest / "pack")
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
# composition module carries the pinned IRIs, atoms, and child modules.
# ---------------------------------------------------------------------------
def test_positive_witness_sync_and_generated_content(tmp_path):
    dest = tmp_path / "pos"
    dest.mkdir()
    pack = _copy_pack(dest)
    proc = _run_sync(pack)
    assert proc.returncode == 0, f"sync refused: {proc.stdout}\n{proc.stderr}"
    out = pack / "generated" / "valve_taxonomy.rs"
    assert out.is_file(), "generated/valve_taxonomy.rs missing after honest sync"
    text = out.read_text(encoding="utf-8")
    for iri, atom, module in PINNED:
        assert f'pub const {atom.upper()}_IRI: &str = "{iri}"' in text, (
            f"pinned IRI constant missing/mutated for {atom}"
        )
        assert f'pub const {atom.upper()}_MODULE: &str = "{module}"' in text, (
            f"pinned child-module constant missing/mutated for {module}"
        )
    assert f'DEFAULT_VALVE_REFUSAL_IRI: &str = "{FUEL_EXHAUSTED_IRI}"' in text, (
        "default-valve emission constant missing/mutated"
    )
    assert "COMPOSITION LAW" in text, "composition-law doc comment missing"
    assert "Strata.Valve.Refusals" in text, (
        "valve module family citation missing from the composition-law doc comment"
    )


# ---------------------------------------------------------------------------
# Court 2 — sync determinism: two honest syncs in separate tmp copies render
# generated/valve_taxonomy.rs byte-identically.
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
        out = pack / "generated" / "valve_taxonomy.rs"
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
    fresh = (pack / "generated" / "valve_taxonomy.rs").read_bytes()
    committed = (STRATUS / "generated" / "valve_taxonomy.rs").read_bytes()
    assert fresh == committed, (
        "committed generated/valve_taxonomy.rs drifted from a fresh sync render"
    )


# ---------------------------------------------------------------------------
# Court 4 — negative witness: corrupting a pinned refusal atom in the
# stratus ontology makes the fail-closed gate refuse the sync (nonzero exit).
# ---------------------------------------------------------------------------
def test_negative_witness_corrupted_atom_refused(tmp_path):
    dest = tmp_path / "neg"
    dest.mkdir()
    pack = _copy_pack(dest)
    ontology = pack / "ontology.ttl"
    text = ontology.read_text(encoding="utf-8")
    corrupted = text.replace('"malformed_frame"', '"malformed_fram"', 1)
    assert corrupted != text, "sabotage did not mutate the ontology"
    ontology.write_text(corrupted, encoding="utf-8")
    proc = _run_sync(pack)
    assert proc.returncode != 0, (
        "corrupted refusal atom was admitted — gate is vacuous"
    )
    assert GATE in (proc.stdout + proc.stderr), (
        "refusal did not name the valve-taxonomy-binding gate"
    )


# ---------------------------------------------------------------------------
# Court 5 — negative witness twin: corrupting the default valve's emission
# edge (different sabotage channel) must also be refused by the same gate.
# ---------------------------------------------------------------------------
def test_negative_witness_corrupted_emission_refused(tmp_path):
    dest = tmp_path / "negem"
    dest.mkdir()
    pack = _copy_pack(dest)
    ontology = pack / "ontology.ttl"
    text = ontology.read_text(encoding="utf-8")
    corrupted = text.replace(
        'st:emitsRefusalClass "' + FUEL_EXHAUSTED_IRI,
        'st:emitsRefusalClass "' + VALVE_NS + "ArenaFailureRefusal",
        1,
    )
    assert corrupted != text, "sabotage did not mutate the ontology"
    ontology.write_text(corrupted, encoding="utf-8")
    proc = _run_sync(pack)
    assert proc.returncode != 0, "corrupted emission was admitted — gate is vacuous"
    assert GATE in (proc.stdout + proc.stderr), (
        "refusal did not name the valve-taxonomy-binding gate"
    )


# ---------------------------------------------------------------------------
# Court 6 — sabotage twin (gate vacuity): corrupt the ParentDiscontinuity
# binding's pinned IRI (first occurrence only, so the emission edge and the
# other three bindings still agree with the hardcoded gate constants, and
# only the wrong_refusal_class branch can see the corruption), then delete
# the gate's wrong_refusal_class branch. The weakened gate must ADMIT that
# ontology — proving the real gate's refusal comes from that branch, not
# from sync failing for unrelated reasons.
# ---------------------------------------------------------------------------
GATE_020 = (STRATUS / "gates" / "020_valve_taxonomy_binding.rq").read_text(
    encoding="utf-8"
)
PD_IRI = VALVE_NS + "ParentDiscontinuityRefusal"


def _gate_without_wrong_class_branch() -> str:
    marker = "  } UNION {\n    # Wrong class: only the four pinned refusal classes may be bound."
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
        text.replace(PD_IRI, PD_IRI + "X", 1), encoding="utf-8"
    )
    gate = pack / "gates" / "020_valve_taxonomy_binding.rq"
    weakened = _gate_without_wrong_class_branch()
    assert weakened != GATE_020, "twin surgery did not mutate the gate"
    gate.write_text(weakened, encoding="utf-8")
    # ggen sync re-reads the gate file directly.
    proc = _run_sync(pack)
    assert proc.returncode == 0, (
        "weakened gate still refused — refusal may come from another branch "
        f"(twin not discriminating): {proc.stdout}\n{proc.stderr}"
    )


# ---------------------------------------------------------------------------
# Court 7 — cross-pack identity (rdflib union court): every pinned IRI in the
# stratus graph resolves to a real valve:RefusalClass in the valve graph with
# the pinned atom and child module; the default valve's emission edge is the
# pinned fuel-exhausted class; register/valve pairing is closed.
# ---------------------------------------------------------------------------
def test_pinned_iris_are_declared_refusal_classes_in_valve_graph():
    stratus = Graph()
    stratus.parse(STRATUS / "ontology.ttl", format="turtle")
    valve = Graph()
    valve.parse(VALVE / "ontology.ttl", format="turtle")

    # Emission edge: DefaultValve emits the pinned fuel-exhausted IRI.
    rows = _query_rows(
        stratus,
        f"""
        PREFIX st: <{ST}>
        SELECT ?iri WHERE {{
          ?v a st:WitnessValve ; st:valveName "default" ; st:emitsRefusalClass ?iri .
          FILTER(STR(?iri) = "{FUEL_EXHAUSTED_IRI}")
        }}""",
    )
    assert rows, "DefaultValve does not emit the pinned refusal IRI"

    # Register/valve pairing closure: every guardedBy edge resolves to a
    # declared WitnessValve carrying an emission edge.
    for register, target in cast(
        Iterable[tuple], stratus.subject_objects(GUARDED_BY)
    ):
        assert (target, RDF_TYPE, URIRef(ST + "WitnessValve")) in stratus, (
            f"{register} guardedBy target is not a declared WitnessValve"
        )
        assert any(str(o) for o in stratus.objects(target, EMITS)), (
            f"guarded valve {target} lacks a refusal emission edge"
        )

    # Cross-pack: each pinned IRI is a valve:RefusalClass in the valve graph
    # with the exact pinned atom and child module.
    for iri, atom, module in PINNED:
        cls = URIRef(iri)
        assert (cls, RDF_TYPE, REFUSAL_CLASS) in valve, (
            f"pinned IRI {iri} is not a valve:RefusalClass in the valve graph"
        )
        atoms = [str(o) for o in valve.objects(cls, ATOM)]
        assert atoms == [atom], (iri, atoms, atom)
        modules = [str(o) for o in valve.objects(cls, MODULE)]
        assert modules == [module], (iri, modules, module)
