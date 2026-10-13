"""Net <-> protocol cross-pack composition courts (PDU envelope law).

The strata-net-pack ontology pins — by IRI literal, no owl:imports, house
style — two strata-protocol-pack CLAP/1.0 wire constants that must ride the
net framed envelope without overflow:
  pdu:PDU_HEADER_LEN      = 64  <= net MAX_MSG_LEN = 65536
  pdu:REFUSAL_RECEIPT_LEN = 32  <= net MAX_MSG_LEN = 65536
Composition law and receipts: packs/strata-net-pack/ontology.ttl
(st:PduEnvelopeBinding individuals CLAP_PDU_ENVELOPE and
REFUSAL_RECEIPT_ENVELOPE), gates/050_pdu_envelope_law.rq,
generated/pdu_envelope.rs.

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
NET = ROOT / "packs" / "strata-net-pack"
PROTOCOL = ROOT / "packs" / "strata-protocol-pack"

PDU_NS = "https://strata.chatman.ai/ontology/pdu#"
HEADER_IRI = PDU_NS + "PDU_HEADER_LEN"
RECEIPT_IRI = PDU_NS + "REFUSAL_RECEIPT_LEN"
HEADER_LEN = 64
RECEIPT_LEN = 32
NET_MAX_MSG_LEN = 65536

EXPECTED_GENERATED_CONSTS = (
    "pub const NET_MAX_MSG_LEN: usize = 65536",
    "pub const PDU_HEADER_LEN: usize = 64",
    "pub const REFUSAL_RECEIPT_LEN: usize = 32",
)


def _ggen_binary() -> str | None:
    return os.environ.get("GGEN_BIN") or shutil.which("ggen")


def _copy_pack(dest: Path) -> Path:
    shutil.copytree(NET, dest / "pack")
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
# composition module carries the pinned constants and the envelope bound.
# ---------------------------------------------------------------------------
def test_positive_witness_sync_and_generated_content(tmp_path):
    dest = tmp_path / "pos"
    dest.mkdir()
    pack = _copy_pack(dest)
    proc = _run_sync(pack)
    assert proc.returncode == 0, f"sync refused: {proc.stdout}\n{proc.stderr}"
    out = pack / "generated" / "pdu_envelope.rs"
    assert out.is_file(), "generated/pdu_envelope.rs missing after honest sync"
    text = out.read_text(encoding="utf-8")
    for const in EXPECTED_GENERATED_CONSTS:
        assert const in text, f"pinned constant missing/mutated: {const}"
    assert "COMPOSITION LAW" in text, "composition-law doc comment missing"
    assert "gates/050_pdu_envelope_law.rq" in text, "gate citation missing"


# ---------------------------------------------------------------------------
# Court 2 — sync determinism: two honest syncs in separate tmp copies render
# generated/pdu_envelope.rs byte-identically.
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
        out = pack / "generated" / "pdu_envelope.rs"
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
    fresh = (pack / "generated" / "pdu_envelope.rs").read_bytes()
    committed = (NET / "generated" / "pdu_envelope.rs").read_bytes()
    assert fresh == committed, (
        "committed generated/pdu_envelope.rs drifted from a fresh sync render"
    )


# ---------------------------------------------------------------------------
# Court 4 — negative witness: corrupting the pinned PDU header length (64 ->
# 63) in the net ontology makes the fail-closed gate refuse the sync
# (nonzero exit, refusal names the 050 gate).
# ---------------------------------------------------------------------------
def test_negative_witness_corrupted_header_len_refused(tmp_path):
    dest = tmp_path / "neg"
    dest.mkdir()
    pack = _copy_pack(dest)
    ontology = pack / "ontology.ttl"
    text = ontology.read_text(encoding="utf-8")
    corrupted = text.replace("st:pduConstantLen 64", "st:pduConstantLen 63", 1)
    assert corrupted != text, "sabotage did not mutate the ontology"
    ontology.write_text(corrupted, encoding="utf-8")
    proc = _run_sync(pack)
    assert proc.returncode != 0, "corrupted PDU header length was admitted — gate is vacuous"
    assert "050_pdu_envelope_law" in (proc.stdout + proc.stderr), (
        "refusal did not name the pdu-envelope-law gate"
    )


# ---------------------------------------------------------------------------
# Court 5 — negative witness twin A: shrinking the net envelope bound
# (MAX_MSG_LEN 65536 -> 32) below the pinned refusal receipt length must
# also be refused (the envelope-law comparison arm fires).
# ---------------------------------------------------------------------------
def test_negative_witness_shrunken_envelope_refused(tmp_path):
    dest = tmp_path / "negenv"
    dest.mkdir()
    pack = _copy_pack(dest)
    ontology = pack / "ontology.ttl"
    text = ontology.read_text(encoding="utf-8")
    corrupted = text.replace('net:maxMsgLen "65536"^^xsd:integer',
                             'net:maxMsgLen "32"^^xsd:integer', 1)
    assert corrupted != text, "sabotage did not mutate the ontology"
    ontology.write_text(corrupted, encoding="utf-8")
    proc = _run_sync(pack)
    assert proc.returncode != 0, "shrunken envelope bound was admitted — gate is vacuous"


# ---------------------------------------------------------------------------
# Court 6 — negative witness twin B: corrupting a pinned constant IRI out of
# the pdu namespace must be refused (wrong_pdu_constant arm).
# ---------------------------------------------------------------------------
def test_negative_witness_corrupted_iri_refused(tmp_path):
    dest = tmp_path / "negiri"
    dest.mkdir()
    pack = _copy_pack(dest)
    ontology = pack / "ontology.ttl"
    text = ontology.read_text(encoding="utf-8")
    corrupted = text.replace(HEADER_IRI, HEADER_IRI + "X", 1)
    assert corrupted != text, "sabotage did not mutate the ontology"
    ontology.write_text(corrupted, encoding="utf-8")
    proc = _run_sync(pack)
    assert proc.returncode != 0, "corrupted pinned IRI was admitted — gate is vacuous"


# ---------------------------------------------------------------------------
# Court 7 — sabotage twin (gate vacuity): corrupt the pinned header length
# consistently (64 -> 63 in the binding; the gate's per-IRI value arm
# removed) so only that branch could fire, then weaken the gate. The
# weakened gate must ADMIT that ontology — proving the real gate's refusal
# comes from that branch, not from sync failing for unrelated reasons.
# ---------------------------------------------------------------------------
GATE_050 = (NET / "gates" / "050_pdu_envelope_law.rq").read_text(encoding="utf-8")


def _gate_without_header_len_branch() -> str:
    marker = "  } UNION {\n    # Per-IRI value pin: header len must be exactly 64."
    start = GATE_050.index(marker) + len("  } UNION {\n")
    end = GATE_050.index("  } UNION {", start)
    weakened = GATE_050[:start] + GATE_050[end:]
    # Collapse the now-empty UNION branch the surgery leaves behind — an
    # empty group matches everything and would itself produce a violation
    # row in the engine.
    return weakened.replace("  } UNION {\n  } UNION {", "  } UNION {", 1)


def test_sabotage_twin_weakened_gate_admits_corrupted_len(tmp_path):
    dest = tmp_path / "twin"
    dest.mkdir()
    pack = _copy_pack(dest)
    ontology = pack / "ontology.ttl"
    text = ontology.read_text(encoding="utf-8")
    ontology.write_text(
        text.replace("st:pduConstantLen 64", "st:pduConstantLen 63", 1),
        encoding="utf-8",
    )
    gate = pack / "gates" / "050_pdu_envelope_law.rq"
    weakened = _gate_without_header_len_branch()
    assert weakened != GATE_050, "twin surgery did not mutate the gate"
    gate.write_text(weakened, encoding="utf-8")
    proc = _run_sync(pack)
    assert proc.returncode == 0, (
        "weakened gate still refused — refusal may come from another branch "
        f"(twin not discriminating): {proc.stdout}\n{proc.stderr}"
    )


# ---------------------------------------------------------------------------
# Court 8 — cross-pack identity: the pinned IRIs in the net graph resolve to
# real pdu:FrameConstant individuals in the protocol graph whose pdu:value
# equals the pinned lengths (real rdflib, both packs).
# ---------------------------------------------------------------------------
def test_pinned_constants_equal_protocol_graph_values():
    net_graph = Graph()
    net_graph.parse(NET / "ontology.ttl", format="turtle")
    protocol = Graph()
    protocol.parse(PROTOCOL / "ontology.ttl", format="turtle")

    # Both pinned IRIs present as string literals in the net graph, on the
    # bindings and on the envelope emission edges.
    pinned = {
        str(o)
        for s, p, o in net_graph
        if str(o) in (HEADER_IRI, RECEIPT_IRI)
    }
    assert {HEADER_IRI, RECEIPT_IRI} <= pinned, "pinned protocol IRIs missing from net graph"

    for iri, pinned_len in ((HEADER_IRI, HEADER_LEN), (RECEIPT_IRI, RECEIPT_LEN)):
        # Emission edge: the net wire law envelopes the pinned constant.
        rows = _query_rows(
            net_graph,
            f"""
            PREFIX st: <https://strata.chatman.ai/ontology#>
            SELECT ?law WHERE {{
              ?law a st:NetWireLaw ; st:envelopesPduConstant "{iri}" .
            }}""",
        )
        assert rows, f"net wire law does not envelope pinned constant {iri}"

        # Cross-pack identity: the IRI is a pdu:FrameConstant in the
        # protocol graph and its value equals the pinned length.
        subject = URIRef(iri)
        rdf_type = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        frame_constant = URIRef(PDU_NS + "FrameConstant")
        assert (subject, rdf_type, frame_constant) in protocol, (
            f"pinned IRI {iri} is not a pdu:FrameConstant in the protocol graph"
        )
        values = [int(str(v)) for v in protocol.objects(subject, URIRef(PDU_NS + "value"))]
        assert values == [pinned_len], (
            f"{iri}: protocol graph value {values} != pinned length {pinned_len}"
        )

    # Envelope law holds on the union graph (rdflib union of both packs).
    union = net_graph + protocol
    rows = _query_rows(
        union,
        f"""
        PREFIX st: <https://strata.chatman.ai/ontology#>
        PREFIX net: <https://strata.chatman.ai/ontology/net#>
        PREFIX pdu: <{PDU_NS}>
        SELECT ?iri ?len WHERE {{
          ?b a st:PduEnvelopeBinding ;
             st:pduConstantIri ?iri ;
             st:pduConstantLen ?pinned .
          ?c a pdu:FrameConstant .
          FILTER(STR(?c) = STR(?iri))
          ?c pdu:value ?real .
          ?law a st:NetWireLaw ; net:maxMsgLen ?maxLen .
          FILTER(xsd:integer(?pinned) = xsd:integer(?real))
          FILTER(xsd:integer(?pinned) <= xsd:integer(?maxLen))
          BIND(?pinned AS ?len)
        }}""",
    )
    assert len(rows) == 2, f"expected 2 closed envelope rows on the union graph, got {rows}"
