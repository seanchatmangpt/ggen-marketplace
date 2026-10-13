"""CAS <-> chain cross-pack composition courts.

Derived invariant (2026-10-13): the strata-chain-pack shared-head KAT
folds four witnessed (pn, ocel) entries with h_0 = 32 zero bytes and
h_{i+1} = BLAKE3(h_i || pn_be || ocel_be || tick_be64) to the pinned
32-byte head 05ea1aa0... — structurally a CAS MerkleCommit chain
(genesis + child_of, depth = entry count) under the shared 32-byte
chained-digest discipline (chain DIGEST_LEN = 32; CAS digest-shape law
^[0-9a-f]{64}$). strata-cas-pack admits the chain KAT head as a CAS
commit-chain witness: ontology individuals st:CasChainWitness /
st:KatEntry, gates/030_cas_chain_composition.rq,
generated/cas_chain.rs. Composition law and receipts:
packs/strata-cas-pack/ontology.ttl, witness.ttl (gate-030 GateRun).

Chicago style: real ggen subprocess syncs in tmp copies, real rdflib
over both pack ontologies, no mocks. Skips carry a "BLOCKED:" reason
prefix when ggen is unavailable.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, cast

import pytest
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
CAS = ROOT / "packs" / "strata-cas-pack"
CHAIN = ROOT / "packs" / "strata-chain-pack"

KAT_HEAD = "05ea1aa096f45968aacb2c996d2b541e4b9fdef24f006e0204e1fa88d33f68a5"
KAT_ENTRIES = [
    ("0x0001000000000001", "0x0A00000000000001"),
    ("0x0002000000000002", "0x0B00000000000002"),
    ("0x0003000000000003", "0x0C00000000000003"),
    ("0x0004000000000004", "0x0D00000000000004"),
]

EXPECTED_GENERATED = (
    f'pub const CHAIN_KAT_HEAD: &str = "{KAT_HEAD}"',
    "pub const CHAIN_DIGEST_LEN: usize = 32",
    "pub const CHAIN_KAT_DEPTH: usize = 4",
    "pub fn cas_chain_closure",
)


def _ggen_binary() -> str | None:
    return os.environ.get("GGEN_BIN") or shutil.which("ggen")


def _copy_pack(dest: Path) -> Path:
    shutil.copytree(CAS, dest / "pack")
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
# Court 1 — positive witness: honest sync exits 0 and generated/cas_chain.rs
# carries the pinned head, the shared digest-length law, the depth law, and
# the composition closure.
# ---------------------------------------------------------------------------
def test_positive_witness_sync_and_generated_content(tmp_path):
    dest = tmp_path / "pos"
    dest.mkdir()
    pack = _copy_pack(dest)
    proc = _run_sync(pack)
    assert proc.returncode == 0, f"sync refused: {proc.stdout}\n{proc.stderr}"
    out = pack / "generated" / "cas_chain.rs"
    assert out.is_file(), "generated/cas_chain.rs missing after honest sync"
    text = out.read_text(encoding="utf-8")
    for expected in EXPECTED_GENERATED:
        assert expected in text, f"pinned content missing/mutated: {expected}"
    assert "COMPOSITION LAW" in text, "composition-law doc comment missing"
    assert "gates/030_cas_chain_composition.rq" in text, "gate citation missing"


# ---------------------------------------------------------------------------
# Court 2 — sync determinism: two honest syncs in separate tmp copies render
# generated/cas_chain.rs byte-identically.
# ---------------------------------------------------------------------------
def test_sync_determinism_two_copies_byte_identical(tmp_path):
    bytes_runs = []
    for i in (1, 2):
        dest = tmp_path / f"det{i}"
        dest.mkdir()
        pack = _copy_pack(dest)
        proc = _run_sync(pack)
        assert proc.returncode == 0, f"sync refused: {proc.stdout}\n{proc.stderr}"
        out = pack / "generated" / "cas_chain.rs"
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
    fresh = (pack / "generated" / "cas_chain.rs").read_bytes()
    committed = (CAS / "generated" / "cas_chain.rs").read_bytes()
    assert fresh == committed, (
        "committed generated/cas_chain.rs drifted from a fresh sync render"
    )


# ---------------------------------------------------------------------------
# Court 4 — negative witness: corrupting the pinned KAT head literal in the
# ontology makes the fail-closed gate refuse the sync (nonzero exit, refusal
# names the 030 gate).
# ---------------------------------------------------------------------------
def test_negative_witness_corrupted_head_refused(tmp_path):
    dest = tmp_path / "neg"
    dest.mkdir()
    pack = _copy_pack(dest)
    ontology = pack / "ontology.ttl"
    text = ontology.read_text(encoding="utf-8")
    corrupted = text.replace(KAT_HEAD, "0" * 63 + "1", 1)
    assert corrupted != text, "sabotage did not mutate the ontology"
    ontology.write_text(corrupted, encoding="utf-8")
    proc = _run_sync(pack)
    assert proc.returncode != 0, "corrupted KAT head was admitted — gate is vacuous"
    assert "030_cas_chain_composition" in (proc.stdout + proc.stderr), (
        "refusal did not name the cas-chain-composition gate"
    )


# ---------------------------------------------------------------------------
# Court 5 — negative witness twin A: wrong shared digest length (32 -> 31)
# must be refused (the digest-length arm fires).
# ---------------------------------------------------------------------------
def test_negative_witness_wrong_digest_len_refused(tmp_path):
    dest = tmp_path / "neglen"
    dest.mkdir()
    pack = _copy_pack(dest)
    ontology = pack / "ontology.ttl"
    text = ontology.read_text(encoding="utf-8")
    corrupted = text.replace(
        'st:chainDigestLen "32"^^xsd:integer',
        'st:chainDigestLen "31"^^xsd:integer', 1)
    assert corrupted != text, "sabotage did not mutate the ontology"
    ontology.write_text(corrupted, encoding="utf-8")
    proc = _run_sync(pack)
    assert proc.returncode != 0, "wrong digest length was admitted — gate is vacuous"


# ---------------------------------------------------------------------------
# Court 6 — negative witness twin B: corrupting one witnessed KAT entry
# (ocel byte flipped) must be refused (the pinned-entry arm fires).
# ---------------------------------------------------------------------------
def test_negative_witness_corrupted_kat_entry_refused(tmp_path):
    dest = tmp_path / "negentry"
    dest.mkdir()
    pack = _copy_pack(dest)
    ontology = pack / "ontology.ttl"
    text = ontology.read_text(encoding="utf-8")
    corrupted = text.replace(
        'st:katPn "0x0004000000000004" ; st:katOcel "0x0D00000000000004"',
        'st:katPn "0x0004000000000004" ; st:katOcel "0x0D00000000000005"', 1)
    assert corrupted != text, "sabotage did not mutate the ontology"
    ontology.write_text(corrupted, encoding="utf-8")
    proc = _run_sync(pack)
    assert proc.returncode != 0, "corrupted KAT entry was admitted — gate is vacuous"


# ---------------------------------------------------------------------------
# Court 7 — sabotage twin (gate vacuity): corrupt the pinned head
# consistently (64-hex 05ea1aa0... -> all-ones 64-hex) while REMOVING the
# exact-pin and malformed-head branches from the gate, so only those arms
# could fire. The weakened gate must ADMIT that ontology — proving the real
# gate's refusal comes from those arms, not from sync failing for unrelated
# reasons.
# ---------------------------------------------------------------------------
GATE_030 = (CAS / "gates" / "030_cas_chain_composition.rq").read_text(encoding="utf-8")


def _gate_without_head_branches() -> str:
    marker = "  } UNION {\n    # Digest-length/domain law"
    start = GATE_030.index(marker) + len("  } UNION {\n")
    end = GATE_030.index("  } UNION {\n    # Depth law", start)
    weakened = GATE_030[:start] + GATE_030[end:]
    # Collapse the now-empty UNION branch the surgery leaves behind — an
    # empty group matches everything and would itself produce a violation
    # row in the engine.
    return weakened.replace("  } UNION {\n  } UNION {", "  } UNION {", 1)


def test_sabotage_twin_weakened_gate_admits_corrupted_head(tmp_path):
    dest = tmp_path / "twin"
    dest.mkdir()
    pack = _copy_pack(dest)
    ontology = pack / "ontology.ttl"
    text = ontology.read_text(encoding="utf-8")
    ontology.write_text(
        text.replace(KAT_HEAD, "f" * 64, 1),
        encoding="utf-8",
    )
    gate = pack / "gates" / "030_cas_chain_composition.rq"
    weakened = _gate_without_head_branches()
    assert weakened != GATE_030, "twin surgery did not mutate the gate"
    gate.write_text(weakened, encoding="utf-8")
    proc = _run_sync(pack)
    assert proc.returncode == 0, (
        "weakened gate still refused — refusal may come from another branch "
        f"(twin not discriminating): {proc.stdout}\n{proc.stderr}"
    )


# ---------------------------------------------------------------------------
# Court 8 — cross-pack identity: the CAS witness head/entries are the SAME
# literals as the chain pack's sw:sharedKatHead / sw:kat-entry-* witnesses
# on the rdflib UNION of both graphs, and the union satisfies the commit-
# chain law (head shape, depth == entry count, 32-byte domain).
# ---------------------------------------------------------------------------
def test_union_graph_identity_with_chain_pack_witnesses():
    cas = Graph()
    cas.parse(CAS / "ontology.ttl", format="turtle")
    chain_witness = Graph()
    chain_witness.parse(CHAIN / "witness.ttl", format="turtle")

    chain_head = {
        str(o) for _, p, o in chain_witness if str(p).endswith("#sharedKatHead")
    }
    assert chain_head == {KAT_HEAD}, f"chain witness head moved: {chain_head}"

    rows = _query_rows(
        cas,
        """
        PREFIX st: <https://strata.chatman.ai/ontology#>
        SELECT ?head ?depth ?len (COUNT(DISTINCT ?e) AS ?n) WHERE {
          ?w a st:CasChainWitness ;
             st:chainKatHead ?head ;
             st:chainKatDepth ?depth ;
             st:chainDigestLen ?len .
          ?e a st:KatEntry .
        } GROUP BY ?head ?depth ?len
        """,
    )
    assert len(rows) == 1, f"expected exactly one CasChainWitness row, got {rows}"
    head, depth, length, n_entries = rows[0]
    assert str(head) == KAT_HEAD
    assert int(depth) == 4 and int(length) == 32 and int(n_entries) == 4

    # Union identity: cas entry set == chain witness entry set.
    def _entries(graph, pn_end, ocel_end):
        pn = {str(o) for _, p, o in graph if str(p).endswith(pn_end)}
        ocel = {str(o) for _, p, o in graph if str(p).endswith(ocel_end)}
        return pn, ocel

    cas_pn, cas_ocel = _entries(cas, "#katPn", "#katOcel")
    chain_pn, chain_ocel = _entries(chain_witness, "#pn", "#ocel")
    assert cas_pn == chain_pn, "KAT pn words diverge across packs"
    assert cas_ocel == chain_ocel, "KAT ocel words diverge across packs"

    # Union law: over cas + chain graphs, the witness binds a head equal to
    # the chain pack's pinned head with the shared 32-byte domain.
    union = cas + chain_witness
    rows = _query_rows(
        union,
        f"""
        PREFIX st: <https://strata.chatman.ai/ontology#>
        PREFIX sw: <https://strata.chatman.ai/ontology/witness#>
        SELECT ?cas_head ?chain_head ?len WHERE {{
          ?w a st:CasChainWitness ;
             st:chainKatHead ?cas_head ;
             st:chainDigestLen ?len .
          ?k sw:sharedKatHead ?chain_head .
          FILTER(?cas_head = ?chain_head)
          FILTER(?len = 32)
        }}""",
    )
    assert len(rows) == 1, f"union identity court did not close: {rows}"
    assert str(rows[0][0]) == KAT_HEAD and str(rows[0][1]) == KAT_HEAD


# ---------------------------------------------------------------------------
# Court 9 — Python-side fold recomputation: the independent blake3 reference
# over the witnessed entries reproduces the pinned head, so the RDF pin and
# the generated Rust court share one ground truth.
# ---------------------------------------------------------------------------
def test_python_fold_reproduces_pinned_head():
    blake3 = pytest.importorskip("blake3", reason="BLOCKED: python blake3 module missing")

    def step(h: bytes, pn: int, ocel: int) -> bytes:
        tick = ocel >> 56
        return blake3.blake3(
            h + pn.to_bytes(8, "big") + ocel.to_bytes(8, "big") + tick.to_bytes(8, "big")
        ).digest()

    h = bytes(32)
    for pn, ocel in KAT_ENTRIES:
        h = step(h, int(pn, 16), int(ocel, 16))
    assert h.hex() == KAT_HEAD, "python fold diverged from the pinned KAT head"
