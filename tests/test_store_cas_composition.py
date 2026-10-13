"""Store <-> CAS cross-pack composition courts.

Derived invariant (2026-10-13): the store's content-address law is
key = SHA-256(value) at KEY_LEN = 32 bytes (so:STORE_CONSTANTS so:keyLen
32), and the pack's content-address KAT (witness.ttl sw:store-kat,
recomputed by verify.py) folds three witnessed payloads under
InMemoryStore::root_digest — SHA-256 over the concatenated 32-byte keys in
BTreeMap lexicographic byte order — to the pinned root a8378cfa.... A root
over concatenated 32-byte digests is structurally a CAS MerkleCommit root
(st:merkleRoot = SHA-256(st:canonicalPayload); the concatenated
keys ARE the canonical payload), so every store key is a valid CAS content
address under the shared digest-shape law ^[0-9a-f]{64}$, and
strata-store-pack admits its own KAT root as a CAS content-address witness:
ontology individuals st:STORE_CAS_WITNESS / st:store-kat-entry-*,
gates/030_store_cas_composition.rq, generated/store_cas.rs. Composition
law and receipts: packs/strata-store-pack/ontology.ttl, witness.ttl
(gate-030 GateRun).

Chicago style: real ggen subprocess syncs in tmp copies, real rdflib over
the pack ontologies, no mocks. Skips carry a "BLOCKED:" reason prefix when
ggen is unavailable.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, cast

import pytest
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "packs" / "strata-store-pack"
CAS = ROOT / "packs" / "strata-cas-pack"

STORE_KAT_ROOT = "a8378cfa4e6e508f54c0287eac99f6e6b07f2fc8b9123bab1f7b2be494f0ef08"

STORE_KAT_ENTRIES = [
    ("strata-store-kat-payload-1",
     "91b739023c976350dacc820d9d8fa02c5617a10f551d89dde3bf4419a54cb367"),
    ("strata-store-kat-payload-2",
     "17dcbd0e84f8a571e7f736b176a3d7160d8cb88d28ef59ce0a51482d5e4ba909"),
    ("strata-store-kat-payload-3",
     "d8de3bf89d034493f711537b87dcf45f0649802194d59bba5db92ca1ee651c28"),
]

EXPECTED_GENERATED = (
    f'pub const STORE_KAT_ROOT: &str = "{STORE_KAT_ROOT}"',
    "pub const STORE_DIGEST_LEN: usize = 32",
    "pub const STORE_KEY_LEN: usize = 32",
    "pub const STORE_KAT_DEPTH: usize = 3",
    "pub fn store_cas_closure",
)


def _ggen_binary() -> str | None:
    return os.environ.get("GGEN_BIN") or shutil.which("ggen")


def _copy_pack(dest: Path) -> Path:
    shutil.copytree(STORE, dest / "pack")
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
# Court 1 — positive witness: honest sync exits 0 and generated/store_cas.rs
# carries the pinned root, the shared digest-length/key-width laws, the depth
# law, and the composition closure.
# ---------------------------------------------------------------------------
def test_positive_witness_sync_and_generated_content(tmp_path):
    dest = tmp_path / "pos"
    dest.mkdir()
    pack = _copy_pack(dest)
    proc = _run_sync(pack)
    assert proc.returncode == 0, f"sync refused: {proc.stdout}\n{proc.stderr}"
    out = pack / "generated" / "store_cas.rs"
    assert out.is_file(), "generated/store_cas.rs missing after honest sync"
    text = out.read_text(encoding="utf-8")
    for expected in EXPECTED_GENERATED:
        assert expected in text, f"pinned content missing/mutated: {expected}"
    assert "COMPOSITION LAW" in text, "composition-law doc comment missing"
    assert "gates/030_store_cas_composition.rq" in text, "gate citation missing"


# ---------------------------------------------------------------------------
# Court 2 — sync determinism: two honest syncs in separate tmp copies render
# generated/store_cas.rs byte-identically.
# ---------------------------------------------------------------------------
def test_sync_determinism_two_copies_byte_identical(tmp_path):
    bytes_runs = []
    for i in (1, 2):
        dest = tmp_path / f"det{i}"
        dest.mkdir()
        pack = _copy_pack(dest)
        proc = _run_sync(pack)
        assert proc.returncode == 0, f"sync refused: {proc.stdout}\n{proc.stderr}"
        out = pack / "generated" / "store_cas.rs"
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
    fresh = (pack / "generated" / "store_cas.rs").read_bytes()
    committed = (STORE / "generated" / "store_cas.rs").read_bytes()
    assert fresh == committed, (
        "committed generated/store_cas.rs drifted from a fresh sync render"
    )


# ---------------------------------------------------------------------------
# Court 4 — negative witness: corrupting the pinned KAT root literal in the
# ontology makes the fail-closed gate refuse the sync (nonzero exit, refusal
# names the 030 gate). The corruption targets the st:storeKatRoot PROPERTY
# literal, not the derivation comment that also quotes the root.
# ---------------------------------------------------------------------------
def test_negative_witness_corrupted_root_refused(tmp_path):
    dest = tmp_path / "neg"
    dest.mkdir()
    pack = _copy_pack(dest)
    ontology = pack / "ontology.ttl"
    text = ontology.read_text(encoding="utf-8")
    corrupted = text.replace(
        f'st:storeKatRoot "{STORE_KAT_ROOT}"',
        'st:storeKatRoot "' + "0" * 63 + '1"', 1)
    assert corrupted != text, "sabotage did not mutate the ontology"
    ontology.write_text(corrupted, encoding="utf-8")
    proc = _run_sync(pack)
    assert proc.returncode != 0, "corrupted KAT root was admitted — gate is vacuous"
    assert "030_store_cas_composition" in (proc.stdout + proc.stderr), (
        "refusal did not name the store-cas-composition gate"
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
        'st:storeDigestLen "32"^^xsd:integer',
        'st:storeDigestLen "31"^^xsd:integer', 1)
    assert corrupted != text, "sabotage did not mutate the ontology"
    ontology.write_text(corrupted, encoding="utf-8")
    proc = _run_sync(pack)
    assert proc.returncode != 0, "wrong digest length was admitted — gate is vacuous"


# ---------------------------------------------------------------------------
# Court 6 — negative witness twin B: corrupting one witnessed KAT entry
# (digest byte flipped) must be refused (the pinned-entry arm fires).
# ---------------------------------------------------------------------------
def test_negative_witness_corrupted_kat_entry_refused(tmp_path):
    dest = tmp_path / "negentry"
    dest.mkdir()
    pack = _copy_pack(dest)
    ontology = pack / "ontology.ttl"
    text = ontology.read_text(encoding="utf-8")
    corrupted = text.replace(
        'st:katDigest "17dcbd0e84f8a571e7f736b176a3d7160d8cb88d28ef59ce0a51482d5e4ba909"',
        'st:katDigest "27dcbd0e84f8a571e7f736b176a3d7160d8cb88d28ef59ce0a51482d5e4ba909"', 1)
    assert corrupted != text, "sabotage did not mutate the ontology"
    ontology.write_text(corrupted, encoding="utf-8")
    proc = _run_sync(pack)
    assert proc.returncode != 0, "corrupted KAT entry was admitted — gate is vacuous"


# ---------------------------------------------------------------------------
# Court 7 — sabotage twin (gate vacuity): corrupt the pinned root
# consistently (64-hex a837cfa4... -> all-ones 64-hex) while REMOVING the
# exact-pin and malformed-root branches from the gate, so only those arms
# could fire. The weakened gate must ADMIT that ontology — proving the real
# gate's refusal comes from those arms, not from sync failing for unrelated
# reasons.
# ---------------------------------------------------------------------------
GATE_030 = (STORE / "gates" / "030_store_cas_composition.rq").read_text(encoding="utf-8")


def _gate_without_root_branches() -> str:
    marker = "  } UNION {\n    # Digest-shape law"
    start = GATE_030.index(marker) + len("  } UNION {\n")
    end = GATE_030.index("  } UNION {\n    # Shared digest-length law", start)
    weakened = GATE_030[:start] + GATE_030[end:]
    # Collapse the now-empty UNION branch the surgery leaves behind — an
    # empty group matches everything and would itself produce a violation
    # row in the engine.
    return weakened.replace("  } UNION {\n  } UNION {", "  } UNION {", 1)


def test_sabotage_twin_weakened_gate_admits_corrupted_root(tmp_path):
    dest = tmp_path / "twin"
    dest.mkdir()
    pack = _copy_pack(dest)
    ontology = pack / "ontology.ttl"
    text = ontology.read_text(encoding="utf-8")
    ontology.write_text(
        text.replace(
            f'st:storeKatRoot "{STORE_KAT_ROOT}"',
            'st:storeKatRoot "' + "f" * 64 + '"', 1),
        encoding="utf-8",
    )
    gate = pack / "gates" / "030_store_cas_composition.rq"
    weakened = _gate_without_root_branches()
    assert weakened != GATE_030, "twin surgery did not mutate the gate"
    gate.write_text(weakened, encoding="utf-8")
    proc = _run_sync(pack)
    assert proc.returncode == 0, (
        "weakened gate still refused — refusal may come from another branch "
        f"(twin not discriminating): {proc.stdout}\n{proc.stderr}"
    )


# ---------------------------------------------------------------------------
# Court 8 — cross-pack identity: the store composition witness root/entries
# are the SAME literals as the pack's own witness.ttl sw:store-kat /
# sw:store-kat-entry-* witnesses on the rdflib UNION of both graphs, and
# the union satisfies the CAS content-address law (root shape, digest len
# 32, 64-hex domain over every entry).
# ---------------------------------------------------------------------------
def test_union_graph_identity_with_witness_kat():
    store = Graph()
    store.parse(STORE / "ontology.ttl", format="turtle")
    store_witness = Graph()
    store_witness.parse(STORE / "witness.ttl", format="turtle")

    witness_root = {
        str(o) for _, p, o in store_witness if str(p).endswith("#storeKatRoot")
    }
    assert witness_root == {STORE_KAT_ROOT}, f"witness root moved: {witness_root}"

    rows = _query_rows(
        store,
        """
        PREFIX st: <https://strata.chatman.ai/ontology#>
        SELECT ?root ?len (COUNT(DISTINCT ?e) AS ?n) WHERE {
          ?w a st:StoreCasWitness ;
             st:storeKatRoot ?root ;
             st:storeDigestLen ?len .
          ?e a st:StoreKatEntry .
        } GROUP BY ?root ?len
        """,
    )
    assert len(rows) == 1, f"expected exactly one StoreCasWitness row, got {rows}"
    root, length, n_entries = rows[0]
    assert str(root) == STORE_KAT_ROOT
    assert int(length) == 32 and int(n_entries) == 3

    # Union identity: ontology entry set == witness.ttl entry set.
    def _entries(graph, payload_end, digest_end):
        payload = {str(o) for _, p, o in graph if str(p).endswith(payload_end)}
        digest = {str(o) for _, p, o in graph if str(p).endswith(digest_end)}
        return payload, digest

    ont_payload, ont_digest = _entries(store, "#katPayload", "#katDigest")
    wit_payload, wit_digest = _entries(store_witness, "#katPayload", "#katDigest")
    assert ont_payload == wit_payload, "KAT payloads diverge across graphs"
    assert ont_digest == wit_digest, "KAT digests diverge across graphs"

    # Union law: over ontology + witness graphs, the witness binds a root
    # equal to the composition witness's pinned root with the 32-byte domain.
    union = store + store_witness
    rows = _query_rows(
        union,
        """
        PREFIX st: <https://strata.chatman.ai/ontology#>
        PREFIX sw: <https://strata.chatman.ai/ontology/witness#>
        SELECT ?ont_root ?wit_root ?len WHERE {
          ?w a st:StoreCasWitness ;
             st:storeKatRoot ?ont_root ;
             st:storeDigestLen ?len .
          ?k sw:storeKatRoot ?wit_root .
          FILTER(?ont_root = ?wit_root)
          FILTER(?len = 32)
        }""",
    )
    assert len(rows) == 1, f"union identity court did not close: {rows}"
    assert str(rows[0][0]) == STORE_KAT_ROOT and str(rows[0][1]) == STORE_KAT_ROOT


# ---------------------------------------------------------------------------
# Court 9 — Python-side fold recomputation: the independent hashlib SHA-256
# reference over the witnessed entries reproduces the pinned root, so the
# RDF pin, verify.py, and the generated Rust court share one ground truth.
# ---------------------------------------------------------------------------
def test_python_fold_reproduces_pinned_root():
    digests = [hashlib.sha256(p.encode("utf-8")).digest() for p, _ in STORE_KAT_ENTRIES]
    for (p, d), k in zip(STORE_KAT_ENTRIES, digests):
        assert k.hex() == d, f"content-address divergence for {p}"
        assert len(k) == 32
    folded = hashlib.sha256(b"".join(sorted(digests))).hexdigest()
    assert folded == STORE_KAT_ROOT, "python fold diverged from the pinned KAT root"
