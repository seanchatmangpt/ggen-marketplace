"""Chicago-style tests for packs/greene-licensing-case-pack.

Real collaborators throughout: the real Turtle files on disk parsed by rdflib,
the real SHACL shapes (this pack's and semantic-case-study-pack's) run by
pyshacl, the real SPARQL gates of both packs, the real gate-court runner as a
subprocess, the real strategic-doctrine catalog bytes, and the real ggen CLI
rendering the packet (skipped by name, never faked, when ggen is not on
PATH). Assertions are on returned state: rows, exit codes, file bytes and
digests. Nothing is mocked.
"""
from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from pyshacl import validate
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, XSD

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "packs"
PACK = PACKS / "greene-licensing-case-pack"
CASE_PACK = PACKS / "semantic-case-study-pack"
CS = Namespace("urn:xaas:case-study:")
GLC = Namespace("https://ggen.dev/ontology/greene-licensing-case#")
GDECK = Namespace("https://ggen.dev/ontology/greene-licensing-case/deck#")
PRES = Namespace("https://ggen.dev/ns/presentation#")
GATES = sorted((PACK / "gates").glob("*.rq"))
CASE_GATES = sorted((CASE_PACK / "gates").glob("*.rq"))
LAB_SUBJECT = "seanchatmangpt/autofde-lab@d6becb595aedac4f18cab84f80bf5aa90e1a45e4"
MARKETPLACE_SUBJECT = "seanchatmangpt/ggen-marketplace@c0f27e5bed97b164ac267f86d8d9d989982319e8"
ADMITTED_LAYOUTS = {"hero_flow", "agenda", "source_chain", "triad", "pipeline", "pairs", "graph",
                    "split", "chain", "stages", "timeline", "flow", "bullets", "three_part"}
FORBIDDEN_RENDERED = re.compile(r"endors|approved by|in partnership", re.IGNORECASE)


def case_graph() -> Graph:
    graph = Graph()
    for path in (PACK / "ontology.ttl", PACK / "ontology" / "greene-case.ttl",
                 PACK / "ontology" / "greene-deck.ttl", PACK / "ontology" / "cs-pres-bridge.ttl",
                 CASE_PACK / "ontology.ttl", PACKS / "pptx-presentation-pack" / "ontology.ttl"):
        graph.parse(path, format="turtle")
    return graph


def rows(graph: Graph, gates: list[Path]) -> dict[str, int]:
    return {gate.stem: len(list(graph.query(gate.read_text(encoding="utf-8")))) for gate in gates}


def test_three_gates_with_exact_stems_and_paired_witnesses() -> None:
    stems = [gate.stem for gate in GATES]
    assert stems == ["050_no_endorsement_language", "060_no_quoted_source_text", "070_letter_author_is_user"]
    for kind in ("pass", "fail"):
        assert sorted(p.stem for p in (PACK / "witnesses" / kind).glob("*.ttl")) == stems


def test_case_graph_conforms_to_both_shape_sets_and_every_gate_returns_zero_rows() -> None:
    graph = case_graph()
    for shapes in (PACK / "ontology" / "shapes.ttl", CASE_PACK / "ontology" / "shapes.ttl"):
        conforms, _, text = validate(graph, shacl_graph=str(shapes), inference="none", advanced=True)
        assert conforms, text
    assert rows(graph, GATES) == {gate.stem: 0 for gate in GATES}
    assert rows(graph, CASE_GATES) == {gate.stem: 0 for gate in CASE_GATES}


def test_claims_are_bound_to_exact_subjects_with_none_authority_and_fixture_ceiling() -> None:
    graph = case_graph()
    case = GLC.case
    assert str(graph.value(case, CS.authorityCeiling)) == "NONE"
    assert str(graph.value(case, CS.evidenceCeiling)) == "REPO_LOCAL_FIXTURE"
    claims = sorted(graph.subjects(CS.claimOf, case), key=str)
    assert [str(graph.value(c, CS.claimId)) for c in claims] == ["C01", "C02", "C03", "C04", "C05"]
    for claim in claims:
        assert str(graph.value(claim, CS.authorityCeiling)) == "NONE"
        assert str(graph.value(claim, CS.evidenceCeiling)) == "REPO_LOCAL_FIXTURE"
        assert str(graph.value(claim, CS.standing)) == "ALIVE_FIXTURE"
        evidence = graph.value(claim, CS.supportedBy)
        assert str(graph.value(evidence, CS.exactSubject)) in {LAB_SUBJECT, MARKETPLACE_SUBJECT}
        assert graph.value(claim, CS.falsifiedBy) is not None
    digests = {str(graph.value(d, GLC.digestKind)): str(graph.value(d, GLC.sha256))
               for d in graph.subjects(RDF.type, GLC.ReceiptDigest)}
    assert len(digests) == 6
    assert all(re.fullmatch(r"[0-9a-f]{64}", value) for value in digests.values())
    labels = sorted(str(graph.value(n, CS.nonClaimId)) for n in graph.subjects(CS.nonClaimOf, case))
    assert labels == ["NC01", "NC02", "NC03", "NC04", "NC05"]


def test_catalog_digest_claim_recomputes_from_the_catalog_bytes_on_disk() -> None:
    graph = case_graph()
    recorded = str(graph.value(GLC["d-catalog"], GLC.sha256))
    catalog = PACKS / "strategic-doctrine-pack" / "generated" / "catalog.json"
    assert hashlib.sha256(catalog.read_bytes()).hexdigest() == recorded


def test_deck_is_ten_slides_each_a_lawful_projection_with_admitted_layout() -> None:
    graph = case_graph()
    slides = sorted(graph.subjects(PRES.slideOf, GDECK.deck), key=lambda s: int(graph.value(s, PRES.order)))
    assert len(slides) == 10
    assert [int(graph.value(s, PRES.order)) for s in slides] == list(range(1, 11))
    for slide in slides:
        assert (slide, RDF.type, PRES.Slide) in graph and (slide, RDF.type, CS.Projection) in graph
        assert str(graph.value(slide, PRES.layout)) in ADMITTED_LAYOUTS
        assert graph.value(slide, PRES.notes) is not None
        renders = list(graph.objects(slide, CS.rendersClaim))
        assert bool(renders) != (graph.value(slide, CS.noClaimReason) is not None)
        assert list(graph.subjects(PRES.blockOf, slide))
    rendered = {str(graph.value(c, CS.claimId)) for c in graph.objects(GDECK.deck, CS.rendersClaim)}
    assert rendered == {"C01", "C02", "C03", "C04", "C05"}


def test_gates_are_not_vacuous_on_the_real_case_graph() -> None:
    graph = case_graph()
    graph.add((GLC.s4, GLC.heading, Literal("Endorsed by the author")))
    assert rows(graph, GATES)["050_no_endorsement_language"] >= 1

    graph = case_graph()
    graph.add((GLC.s2, GLC.heading, Literal("Line one\n> a quotation block")))
    assert rows(graph, GATES)["060_no_quoted_source_text"] >= 1

    graph = case_graph()
    graph.add((GLC.s2, GLC.quotedText, Literal("x")))
    assert rows(graph, GATES)["060_no_quoted_source_text"] >= 1

    graph = case_graph()
    graph.set((GLC.letter, GLC.sender, GLC.ghostwriter))
    assert rows(graph, GATES)["070_letter_author_is_user"] == 1

    graph = case_graph()
    graph.add((GLC.letter, GLC.sentOn, Literal("2026-09-27", datatype=XSD.date)))
    assert rows(graph, GATES)["070_letter_author_is_user"] == 1

    graph = case_graph()
    graph.set((GLC.letter, GLC.letterStatus, Literal("FINAL")))
    assert rows(graph, GATES)["070_letter_author_is_user"] == 1

    graph = case_graph()
    graph.set((GLC.c01, CS.authorityCeiling, Literal("DO")))
    assert rows(graph, CASE_GATES)["040_authority_ceiling_select_construct_only"] == 1


@pytest.mark.parametrize("gate", GATES, ids=lambda g: g.stem)
@pytest.mark.parametrize("expectation", ["pass", "fail"])
def test_court_runner_observes_each_witness_expectation(gate: Path, expectation: str) -> None:
    witness = PACK / "witnesses" / expectation / f"{gate.stem}.ttl"
    result = subprocess.run(
        [sys.executable, "runners/semantic_runner.py", "--gate", str(gate), "--witness", str(witness),
         "--expectation", expectation],
        cwd=PACK, text=True, capture_output=True,
    )
    assert result.returncode == 0, result.stderr


def test_court_runner_refuses_a_fail_witness_judged_against_the_wrong_gate() -> None:
    result = subprocess.run(
        [sys.executable, "runners/semantic_runner.py", "--gate", str(GATES[0]),
         "--witness", str(PACK / "witnesses" / "fail" / f"{GATES[2].stem}.ttl"), "--expectation", "fail"],
        cwd=PACK, text=True, capture_output=True,
    )
    assert result.returncode == 2
    assert "REFUSED_EXPECTED_GATE_DID_NOT_FIRE" in result.stderr


def test_stale_no_presentation_pack_statement_is_gone() -> None:
    for path in (CASE_PACK / "ontology.ttl", CASE_PACK / "templates" / "slide-facts.md.tmpl"):
        text = path.read_text(encoding="utf-8")
        assert "no pptx-presentation-pack" not in text
        assert "cs-pres-bridge.ttl" in text


@pytest.mark.skipif(shutil.which("ggen") is None, reason="ggen CLI not on PATH; the packet is rendered only by real ggen")
def test_real_ggen_renders_packet_deterministically_without_forbidden_text(tmp_path: Path) -> None:
    outputs = []
    for run in ("a", "b"):
        consumer = tmp_path / run
        result = subprocess.run([sys.executable, str(PACK / "runners" / "render_packet.py"), "--consumer", str(consumer)],
                                text=True, capture_output=True)
        assert result.returncode == 0, result.stdout + result.stderr
        outputs.append({p.name: p.read_bytes() for p in sorted((consumer / "greene-licensing").glob("*.md"))})
    assert outputs[0] == outputs[1]
    assert sorted(outputs[0]) == ["appendix.md", "demo-spec.md", "letter.md", "rights-table.md"]
    for name, data in outputs[0].items():
        text = data.decode("utf-8")
        assert not FORBIDDEN_RENDERED.search(text), name
        assert not any(line.lstrip().startswith(">") for line in text.splitlines()), name
    letter = outputs[0]["letter.md"].decode("utf-8")
    assert "PROPOSAL_DRAFT" in letter and letter.rstrip().splitlines()[-3] == "Sender and author of this proposal draft"
    assert "Sean Chatman" in letter
    assert len(letter.split()) <= 900
    appendix = outputs[0]["appendix.md"].decode("utf-8")
    assert "f10e2294dbd5c6d7ee1c8b97b3af36fcb706326e6a6dc7ed88f5c8db441c8665" in appendix
    assert "9f1d03a3188430dde6c8fad00c63714daff73aa3600229d9f521ec41e2edc6d4" in appendix
