"""Alignment court: industry-closure-ledger-pack -> main's industry-closure / sjira packs.

Chicago style: real Turtle on disk parsed by rdflib and the real ledger gate 050.
Proves (PARTIAL_ALIVE, rdflib only): every aligned IRI exists in its source ontology,
the alignment is one-directional, and a CLOSED value from main's vocabulary does not
substitute for ledger evidence. No ggen binary is involved; nothing here is ALIVE.
"""
from __future__ import annotations

import sys
from pathlib import Path

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, SKOS

TESTS = Path(__file__).resolve().parent
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

import ic_support as S  # noqa: E402

PACKS = S.PACKS
ALIGNMENT = S.PACK / "ontology" / "alignment-industry-closure.ttl"
MAIN_ONTOLOGY = PACKS / "industry-closure-pack" / "ontology.ttl"
SJIRA_ONTOLOGY = PACKS / "sjira-marketplace-feedback-pack" / "ontology.ttl"
GATE_050 = S.PACK / "gates" / "050_coverage_chain.rq"
PASS_050 = S.PACK / "witnesses" / "pass" / "050_coverage_chain.ttl"

LEDGER_NS = S.IC
MAIN_NS = "https://ggen.dev/ontology/industry-closure#"
SJIRA_NS = "https://ggen.dev/ontology/sjira-marketplace-feedback#"
ICM = Namespace(MAIN_NS)


def _alignment() -> Graph:
    return Graph().parse(ALIGNMENT, format="turtle")


def _terms(graph: Graph) -> set[URIRef]:
    return {t for triple in graph for t in triple if isinstance(t, URIRef)}


def _defined(graph: Graph, iri: URIRef) -> bool:
    """A term exists in an ontology file when it is the subject of at least one triple."""
    return (iri, None, None) in graph


def _aligned_pairs(graph: Graph) -> list[tuple[URIRef, URIRef, URIRef]]:
    preds = (SKOS.closeMatch, SKOS.narrowMatch, SKOS.relatedMatch)
    return [(s, p, o) for p in preds for s, o in graph.subject_objects(p)]


def test_alignment_parses_and_has_mappings():
    assert len(_aligned_pairs(_alignment())) >= 4


def test_every_aligned_iri_exists_in_its_ontology_file():
    align = _alignment()
    ledger = Graph().parse(S.ONTOLOGY, format="turtle")
    main = Graph().parse(MAIN_ONTOLOGY, format="turtle")
    sjira = Graph().parse(SJIRA_ONTOLOGY, format="turtle")
    by_ns = {LEDGER_NS: ledger, MAIN_NS: main, SJIRA_NS: sjira}
    for s, _p, o in _aligned_pairs(align):
        for term in (s, o):
            ns = next((n for n in by_ns if str(term).startswith(n)), None)
            assert ns is not None, f"{term} is in no known namespace"
            assert _defined(by_ns[ns], term), f"drift: {term} not defined in its ontology file"


def test_each_mapping_joins_the_ledger_to_exactly_one_other_pack():
    for s, p, o in _aligned_pairs(_alignment()):
        sides = {str(s).startswith(LEDGER_NS), str(o).startswith(LEDGER_NS)}
        assert sides == {True, False}, f"{s} {p} {o} must cross packs"


def test_no_equivalence_or_subsumption_is_claimed_over_main_terms():
    forbidden = {
        URIRef("http://www.w3.org/2002/07/owl#equivalentClass"),
        URIRef("http://www.w3.org/2002/07/owl#sameAs"),
        URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),
        SKOS.exactMatch,
    }
    for _s, p, _o in _alignment():
        assert p not in forbidden, f"{p} would over-claim equivalence with main"


def test_alignment_is_one_directional_and_not_imported():
    align = _alignment()
    # Mappings are only asserted on ledger-or-main subjects that live in this file, and the
    # file never types or redefines a main/sjira term (no rdf:type, no rdfs:* on foreign IRIs).
    foreign_defs = [
        (s, p) for s, p, _o in align
        if not str(s).startswith(LEDGER_NS) and p in (RDF.type, URIRef("http://www.w3.org/2000/01/rdf-schema#label"))
    ]
    assert foreign_defs == []
    # The alignment is not loaded by manufacture.
    ggen_toml = (S.PACK / "ggen.toml").read_text(encoding="utf-8")
    assert "alignment-industry-closure" not in ggen_toml
    # No other pack mentions the ledger namespace or the alignment file.
    for pack in ("industry-closure-pack", "sjira-marketplace-feedback-pack"):
        for path in (PACKS / pack).rglob("*"):
            if path.is_file():
                text = path.read_text(encoding="utf-8", errors="ignore")
                assert LEDGER_NS not in text and "alignment-industry-closure" not in text, path


def test_main_closed_assessment_is_not_ledger_coverage_without_evidence():
    # Baseline: the pass witness is lawful under gate 050.
    base = S.world(PASS_050)
    assert S.gate_rows(base, GATE_050) == []

    # Remove ledger evidence for the head coverage, then assert a main-vocabulary CLOSED
    # assessment for the same requirement. The assessment must not fill the gap.
    EX = "https://example.invalid/synthetic/"
    bare = Graph()
    for t in base:
        bare.add(t)
    for ev in list(bare.subjects(RDF.type, URIRef(LEDGER_NS + "ExecutionEvidence"))):
        for t in list(bare.triples((ev, None, None))):
            bare.remove(t)
    refused = S.gate_reasons(bare, GATE_050)
    assert "REFUSED:IC_COVERAGE_EVIDENCE_MISSING" in refused

    assessment = URIRef(EX + "mainAssessmentA")
    bare.add((assessment, RDF.type, ICM.ClosureAssessment))
    bare.add((assessment, ICM.closureState, ICM.CLOSED))
    bare.parse(ALIGNMENT, format="turtle")
    assert "REFUSED:IC_COVERAGE_EVIDENCE_MISSING" in S.gate_reasons(bare, GATE_050)

    # With ledger evidence restored the same graph is accepted again.
    restored = S.merged(Graph(), PASS_050)
    restored.add((assessment, RDF.type, ICM.ClosureAssessment))
    restored.add((assessment, ICM.closureState, ICM.CLOSED))
    assert S.gate_rows(restored, GATE_050) == []
