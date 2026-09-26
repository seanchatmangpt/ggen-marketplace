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
import json
import os
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
FORBIDDEN_RENDERED = re.compile(
    r"endors|approved\s+by|approval\s+of\s+the\s+author|in\s+partnership|partnered\s+with|official\s+partner"
    r"|authori[sz]ed\s+by|sanctioned\s+by|sponsored\s+by|on\s+behalf\s+of\s+the\s+author"
    r"|with\s+the\s+blessing\s+of|officially\s+(supported|recogni[sz]ed|licensed|affiliated)"
    r"|(backed|supported|recommended|blessed|vetted|certified|commissioned)\s+by\s+(the\s+)?"
    r"(author|publisher|estate|rights\s+holder)", re.IGNORECASE)
INVISIBLE = re.compile("[\u00ad\u200b-\u200f\u2060-\u2064\ufeff]")
TYPOGRAPHIC_QUOTES = re.compile("[\u201c\u201d\u201e\u201f\u2018\u201a\u201b\u00ab\u00bb\u2039\u203a\u300c-\u300f]")


def normalized(text: str) -> str:
    """Same normalization gate 050 applies: strip invisible characters, join soft-wrapped words."""
    return re.sub(r"-[ \t]*\r?\n[ \t]*", "", INVISIBLE.sub("", text))
LAB_SHA = LAB_SUBJECT.rsplit("@", 1)[1]
HEX64 = re.compile(r"\b[0-9a-f]{64}\b")
ABBREVIATED = re.compile(r"\b([0-9a-f]{8})\.\.\.([0-9a-f]{4,})\b")


def case_graph() -> Graph:
    graph = Graph()
    for path in (PACK / "ontology.ttl", PACK / "ontology" / "greene-case.ttl",
                 PACK / "ontology" / "greene-deck.ttl", PACK / "ontology" / "cs-pres-bridge.ttl",
                 CASE_PACK / "ontology.ttl", PACKS / "pptx-presentation-pack" / "ontology.ttl"):
        graph.parse(path, format="turtle")
    return graph


def recorded_digests(graph: Graph) -> dict[str, str]:
    return {str(graph.value(d, GLC.digestKind)): str(graph.value(d, GLC.sha256))
            for d in graph.subjects(RDF.type, GLC.ReceiptDigest)}


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
        assert not FORBIDDEN_RENDERED.search(normalized(text)), name
        assert not INVISIBLE.search(text), name
        assert not TYPOGRAPHIC_QUOTES.search(text), name
        assert not any(line.lstrip().startswith((">", "&gt;")) for line in text.splitlines()), name
    letter = outputs[0]["letter.md"].decode("utf-8")
    assert "PROPOSAL_DRAFT" in letter and letter.rstrip().splitlines()[-3] == "Sender and author of this proposal draft"
    assert "Sean Chatman" in letter
    assert len(letter.split()) <= 900
    appendix = outputs[0]["appendix.md"].decode("utf-8")
    for digest in recorded_digests(case_graph()).values():
        assert digest in appendix


def test_every_digest_copy_in_the_pack_is_a_recorded_digest() -> None:
    """Witnesses, deck bodies and templates may only repeat the graph's own digests.

    A transposed copy anywhere (the report.json digest was once recorded with
    digits 4-6 swapped in six files) is refused: every full 64-hex literal must
    equal a recorded glc:sha256 and every abbreviated 8...N form must be the
    prefix/suffix of one.
    """
    recorded = set(recorded_digests(case_graph()).values())
    assert len(recorded) == 6
    seen_full = seen_short = 0
    for path in sorted(PACK.rglob("*")):
        if path.suffix not in {".ttl", ".tmpl", ".md", ".toml", ".rq"}:
            continue
        text = path.read_text(encoding="utf-8")
        for digest in HEX64.findall(text):
            seen_full += 1
            assert digest in recorded, f"{path.relative_to(PACK)}: {digest} is not a recorded digest"
        for head, tail in ABBREVIATED.findall(text):
            seen_short += 1
            assert any(d.startswith(head) and d.endswith(tail) for d in recorded), \
                f"{path.relative_to(PACK)}: {head}...{tail} abbreviates no recorded digest"
    assert seen_full >= 12 and seen_short >= 4


def autofde_lab_repo() -> Path | None:
    candidates = [os.environ.get("AUTOFDE_LAB_REPO"), str(ROOT.parent / "autofde-lab"),
                  str(Path.home() / "autofde-lab")]
    for candidate in candidates:
        if not candidate:
            continue
        repo = Path(candidate)
        probe = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{LAB_SHA}^{{commit}}"],
                               capture_output=True) if (repo / ".git").exists() else None
        if probe is not None and probe.returncode == 0:
            return repo
    return None


LAB_REPO = autofde_lab_repo()
LAB_DRIVER = """
import sys
sys.meta_path = [f for f in sys.meta_path if "editable" not in repr(f).lower()]
sys.path = [p for p in sys.path if not p.rstrip("/").endswith("autofde-lab/src")]
sys.path.insert(0, sys.argv[1])
import autofde_lab.simulation.doctrine_lab as lab
assert lab.__file__.startswith(sys.argv[1]), lab.__file__
from autofde_lab.simulation.doctrine_lab.__main__ import main
raise SystemExit(main(["--out", sys.argv[2], "--replay"]))
"""


@pytest.mark.skipif(LAB_REPO is None or shutil.which("git") is None,
                    reason="autofde-lab checkout holding the bound commit not found (set AUTOFDE_LAB_REPO)")
def test_lab_digests_recompute_from_a_real_run_of_the_bound_autofde_lab_commit(tmp_path: Path) -> None:
    """Run the doctrine lab at the exact bound commit and recompute C01-C04's digests.

    The lab source is materialized by `git archive <sha>` (never the working
    tree), run twice in separate processes with --replay, and every recorded
    lab digest must equal the recomputed value. The interpreter is the lab's
    own virtualenv when present (AUTOFDE_LAB_PYTHON overrides).
    """
    assert LAB_REPO is not None
    source = tmp_path / "lab"
    source.mkdir()
    archive = subprocess.run(["git", "-C", str(LAB_REPO), "archive", LAB_SHA, "--", "src/autofde_lab"],
                             capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(source)], input=archive, check=True)
    venv = LAB_REPO / ".venv" / "bin" / "python"
    python = os.environ.get("AUTOFDE_LAB_PYTHON") or (str(venv) if venv.exists() else sys.executable)
    runs = []
    for name in ("run1", "run2"):
        out = tmp_path / name
        result = subprocess.run([python, "-I", "-c", LAB_DRIVER, str(source / "src"), str(out)],
                                text=True, capture_output=True)
        assert result.returncode == 0, result.stdout + result.stderr
        summary = json.loads(result.stdout)
        runs.append({
            "ledger tail digest": summary["ledger"]["tail_digest"],
            "matrix digest": summary["matrix_digest"],
            "report digest": summary["report_digest"],
            "report.json file sha256": hashlib.sha256((out / "report.json").read_bytes()).hexdigest(),
            "ledger.jsonl file sha256": hashlib.sha256((out / "ledger.jsonl").read_bytes()).hexdigest(),
        })
        assert summary["ledger"]["records"] == 252 and summary["ledger"]["valid"] is True
        assert summary["verify_run"] == {"failures": [], "replayed": True, "valid": True}
        assert summary["clusters"] == 2
    assert runs[0] == runs[1]
    recorded = recorded_digests(case_graph())
    assert {kind: recorded[kind] for kind in runs[0]} == runs[0]


def test_court_runner_refuses_a_pass_witness_whose_graph_fires_a_gate(tmp_path: Path) -> None:
    """The pass branch refuses gate rows even when SHACL conforms."""
    base = (PACK / "witnesses" / "pass" / f"{GATES[0].stem}.ttl").read_text(encoding="utf-8")
    witness = tmp_path / "pass_with_gate_rows.ttl"
    witness.write_text(base + '\n<urn:example:stray> <urn:example:note> "Sponsored  by a publisher" .\n',
                       encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "runners/semantic_runner.py", "--gate", str(GATES[0]), "--witness", str(witness),
         "--expectation", "pass"],
        cwd=PACK, text=True, capture_output=True,
    )
    assert result.returncode == 2, result.stdout + result.stderr
    refusal = json.loads(result.stderr.strip().splitlines()[-1])
    assert refusal["refusal"] == "REFUSED_GATE_ROWS_ON_PASS"
    assert list(refusal["gates"]) == ["050_no_endorsement_language"]


@pytest.mark.parametrize("phrase", ["Approved  by the author", "in\tpartnership with", "sponsored\nby a press",
                                    "on behalf  of the author"])
def test_gate_050_matches_backing_phrases_across_any_whitespace(phrase: str) -> None:
    graph = case_graph()
    graph.add((GLC.s4, GLC.body, Literal(phrase)))
    assert rows(graph, GATES)["050_no_endorsement_language"] >= 1


@pytest.mark.parametrize("phrase", [
    "end\u200borsed by the author",            # zero-width space inside the stem
    "end\u00adorsed by the author",            # soft hyphen inside the stem
    "endor-\nsed by the author",               # soft-wrapped word
    "endor- \r\n  sed by the author",         # soft wrap with CRLF and indentation
    "backed by the author",
    "officially supported by the publisher",
    "supported by the rights holder",
    "vetted by the estate",
    "approved\u00a0by the author",             # no-break space between words
])
def test_gate_050_closes_known_evasions(phrase: str) -> None:
    graph = case_graph()
    graph.add((GLC.s4, GLC.body, Literal(phrase)))
    assert rows(graph, GATES)["050_no_endorsement_language"] >= 1
    assert FORBIDDEN_RENDERED.search(normalized(phrase)) is not None


def test_gate_050_refuses_an_invisible_character_even_without_backing_language() -> None:
    graph = case_graph()
    graph.add((GLC.s4, GLC.body, Literal("an ordinary\u2060sentence")))
    reasons = {str(r[2]) for r in graph.query(GATES[0].read_text(encoding="utf-8"))}
    assert reasons == {"invisible-format-character"}


@pytest.mark.parametrize("literal", [
    "\u2018a long excerpt copied verbatim from the source text\u2019",  # single typographic quotes
    "\u201aa low opening quote",
    "\u2039angle quotes\u203a",
    '"abcdefghijklmnopqrstuvwx"',                                    # 24-char straight-quoted span
    '"abcdefghijkl"',                                                # 12-char straight-quoted span
    'a "two words" b',                                               # multi-word span of any length
    "&gt; quoted",                                                   # escaped blockquote marker
    "line one\n  &#62; quoted",
])
def test_gate_060_closes_known_evasions(literal: str) -> None:
    graph = case_graph()
    graph.add((GLC.s4, GLC.body, Literal(literal)))
    assert rows(graph, GATES)["060_no_quoted_source_text"] >= 1


@pytest.mark.parametrize("literal", ["the author\u2019s title", 'the "ALIVE" label', "a > b in prose",
                                     'One of "available", "falsified", or "selected" -- a state.',
                                     "no affiliation implied with any author"])
def test_gates_050_and_060_admit_ordinary_prose(literal: str) -> None:
    graph = case_graph()
    graph.add((GLC.s4, GLC.body, Literal(literal)))
    counts = rows(graph, GATES)
    assert counts["050_no_endorsement_language"] == 0 and counts["060_no_quoted_source_text"] == 0


def test_gates_admit_the_full_import_union_ggen_evaluates() -> None:
    """ggen runs pack gates over the UNION graph, imports included (FM-PACK-013).

    The rdflib case graph above omits evidence-standing-pack and
    decision-optionality-pack; this union adds them, so a gate that would
    refuse an imported ontology's own comments fails here, not only under ggen.
    """
    graph = case_graph()
    for pack in ("evidence-standing-pack", "decision-optionality-pack"):
        graph.parse(PACKS / pack / "ontology.ttl", format="turtle")
    assert rows(graph, GATES) == {gate.stem: 0 for gate in GATES}
