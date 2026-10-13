"""Known-answer-test (KAT) court for the affidavit chain law (lane: affidavit KAT).

The chain law exists as two hand-duplicated copies -- the generated module in
the ggen example consumer (~/ggen/examples/affidavit-verify/src/affidavit_chain.rs)
and this marketplace repo's pack template
(packs/affidavit-pack/templates/affidavit_chain.rs.tmpl).
This court pins the law with REAL computed blake3 known-answer vectors:

1. the committed KAT fixture (packs/affidavit-pack/kat/affidavit_chain_kat.json)
   is present and well-formed;
2. every vector's expected chain head is reproduced by recomputing the fold
   blake3(prev_hex_ascii || canonical_json(event)) in Python (real blake3, no
   mocks);
3. the fail-closed gate (gates/010_affidavit_kat_gate.rq) returns zero rows
   against the real ontology (rdflib);
4. a sabotage twin: flipping one byte in a vector makes the recompute court
   fail;
5. a drift meta-test vs the sibling ggen example copy of the law
   (BLOCKED:-skip when that repo is absent).

Chicago style: real files, real hashes, real SPARQL, no mocks.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

pytest.importorskip("rdflib")
try:
    import blake3 as _blake3
except ImportError:  # pragma: no cover
    _blake3 = None

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "affidavit-pack"
KAT_PATH = PACK / "kat" / "affidavit_chain_kat.json"
ONTOLOGY = PACK / "ontology.ttl"
GATE = PACK / "gates" / "010_affidavit_kat_gate.rq"
# Sibling hand-duplicated copy of the same law (different repo, read-only).
SIBLING = (
    Path.home()
    / "ggen"
    / "examples"
    / "affidavit-verify"
    / "src"
    / "affidavit_chain.rs"
)

HEX32 = re.compile(r"^[0-9a-f]{64}$")


def _blake3_hex(data: bytes) -> str:
    if _blake3 is None:
        pytest.skip(
            "BLOCKED: python blake3 package unavailable; KAT recompute needs real blake3"
        )
    return _blake3.blake3(data).hexdigest()


def _canonical_json(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _fold(prev_hex: str, event: dict) -> str:
    """The pack's law: blake3(prev.as_hex().as_bytes() || canonical_bytes(event))."""
    return _blake3_hex(prev_hex.encode("ascii") + _canonical_json(event))


def _load_kat() -> dict:
    return json.loads(KAT_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 1. KAT fixture: presence + shape + genesis
# ---------------------------------------------------------------------------

def test_kat_fixture_present_and_wellformed() -> None:
    payload = _load_kat()
    assert payload["law"] == (
        "blake3(prev_hex_ascii || canonical_json(event)), genesis = blake3(seed)"
    )
    seed = payload["genesis_seed"]
    assert seed == "affidavit-v0.1.0-genesis"
    assert payload["genesis_seed_hex"] == seed.encode().hex()
    assert _blake3_hex(seed.encode()) == payload["genesis_head"]
    assert payload["vector_count"] == len(payload["vectors"]) == 4
    for vec in payload["vectors"]:
        assert len(vec["canonical_bytes_hex"]) % 2 == 0
        assert HEX32.fullmatch(vec["chain_head"])
        # round-trip: hex decodes to the sorted-key canonical JSON of the event
        assert bytes.fromhex(vec["canonical_bytes_hex"]) == _canonical_json(vec["event"])


# ---------------------------------------------------------------------------
# 2. Real recompute of the chain law over the vectors
# ---------------------------------------------------------------------------

def test_kat_vectors_recompute_via_blake3() -> None:
    payload = _load_kat()
    acc = payload["genesis_head"]
    for i, vec in enumerate(payload["vectors"], start=1):
        assert vec["canonical_bytes_hex"] == _canonical_json(vec["event"]).hex()
        acc = _fold(acc, vec["event"])
        assert acc == vec["chain_head"], f"vector {i} chain head mismatch"


# ---------------------------------------------------------------------------
# 3. Fail-closed gate: zero rows over the real ontology
# ---------------------------------------------------------------------------

def test_kat_gate_returns_zero_rows_over_real_ontology() -> None:
    from rdflib import Graph

    graph = Graph().parse(ONTOLOGY, format="turtle")
    gate_sparql = GATE.read_text(encoding="utf-8")
    rows = list(graph.query(gate_sparql))
    assert rows == [], (
        "KAT gate must return zero rows over the committed ontology; got: "
        + repr([tuple(r) for r in rows])
    )


# ---------------------------------------------------------------------------
# 4. Sabotage twin: a flipped byte in a vector must be caught
# ---------------------------------------------------------------------------

def test_sabotage_twin_flipped_vector_byte_is_detected() -> None:
    payload = _load_kat()
    victim = dict(payload["vectors"][0])
    flipped = (
        ("0" if victim["chain_head"][0] != "0" else "1")
        + victim["chain_head"][1:]
    )
    victim["chain_head"] = flipped

    acc = payload["genesis_head"]
    detected = False
    for vec in payload["vectors"]:
        cur = victim if vec is payload["vectors"][0] else vec
        acc = _fold(acc, cur["event"])
        if acc != cur["chain_head"]:
            detected = True
            break
    assert detected, "court must catch a single flipped chain-head byte"


def test_sabotage_twin_missing_seed_constant_is_detected_by_gate() -> None:
    from rdflib import Graph
    from rdflib.namespace import RDF

    graph = Graph().parse(ONTOLOGY, format="turtle")
    seed_iri = None
    for s in graph.subjects(RDF.type, None):
        if str(s).endswith("katSeed"):
            seed_iri = s
            break
    assert seed_iri is not None, "ontology must contain the afd:katSeed individual"

    AFD = "http://seanchatmangpt.github.io/packs/affidavit#"
    graph.remove((seed_iri, None, None))
    rows = list(graph.query(GATE.read_text(encoding="utf-8")))
    problems = [str(row["problem"]) for row in rows]
    assert problems, "gate must fire when the KatSeed constants are stripped"
    assert any("KatSeed" in p for p in problems), problems


# ---------------------------------------------------------------------------
# 5. Drift meta-test vs the sibling ggen example copy of the law
# ---------------------------------------------------------------------------

def test_sibling_law_copy_in_ggen_is_absent_or_identical() -> None:
    if not SIBLING.exists():
        pytest.skip("BLOCKED: sibling ggen example not present at ~/ggen")
    template = (PACK / "templates" / "affidavit_chain.rs.tmpl").read_text(
        encoding="utf-8"
    )
    # strip the ggen frontmatter (--- ... ---) from the template
    body = template.split("---\n", 2)[2]
    sibling = SIBLING.read_text(encoding="utf-8")
    assert body == sibling, (
        "the two hand-duplicated copies of the affidavit chain law have drifted: "
        f"{PACK / 'templates' / 'affidavit_chain.rs.tmpl'} vs {SIBLING}"
    )
