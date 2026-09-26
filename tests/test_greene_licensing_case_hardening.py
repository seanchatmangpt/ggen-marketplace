"""Adversarial hardening for packs/greene-licensing-case-pack (v26.9.26).

Chicago style, real collaborators only: the pack's real Turtle files parsed by
rdflib, the real gates/*.rq, the real runners/semantic_runner.py run as a
subprocess, and the real bench/bench_gates.py. Every case below was an
observed evasion or crash on PR #509 head b5821eea before the gates and
runner were hardened; each is now a permanent guard.

Classes covered:
  * spelling evasions of gate 050 (confusable scripts, fullwidth, combining
    marks, U+2010/U+2011 soft wraps);
  * carrier evasions of gate 060 (HTML character references, HTML quotation
    elements, single-quoted multi-word spans);
  * structural evasions of gate 070 (second status, untyped letter, subclass
    of glc:Letter under no-inference evaluation, a second glc:User);
  * runner input (malformed witness, foreign same-stem gate, unparseable
    gate) -- typed REFUSED_STRUCTURAL, never a traceback;
  * duplicate delivery and reordering of witness statements (verdict and
    rows are invariant);
  * catastrophic regex backtracking (adversarial literals are bounded);
  * a benchmark regression bound against the committed bench receipt.
"""
from __future__ import annotations

import hashlib
import json
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest
from rdflib import Graph, Literal
from rdflib.compare import isomorphic
from rdflib.namespace import RDF, RDFS

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_greene_licensing_case_pack as base  # noqa: E402

PACK = base.PACK
GATES = base.GATES
GLC = base.GLC
RUNNER = PACK / "runners" / "semantic_runner.py"
BENCH = PACK / "bench" / "bench_gates.py"
RECEIPT = PACK / "bench" / "receipt-v26.9.26.json"


def reasons(graph: Graph, stem: str) -> set[str]:
    gate = next(g for g in GATES if g.stem == stem)
    return {str(row[-1]) for row in graph.query(gate.read_text(encoding="utf-8"))}


def with_body(text: str) -> Graph:
    graph = base.case_graph()
    graph.add((GLC.s4, GLC.body, Literal(text)))
    return graph


def run_runner(*args: str, cwd: Path = PACK, runner: Path = RUNNER) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(runner), *args], cwd=cwd, text=True, capture_output=True)


# ---------------------------------------------------------------- gate 050

@pytest.mark.parametrize("literal", [
    "еndorsed by the author",                     # Cyrillic small ie for e
    "ｅｎｄｏｒｓｅｄ",  # fullwidth letters
    "endórsed",                                  # combining acute accent
    "endórsed",                                   # precomposed accented Latin
    "ᴇndorsed",                                   # small-capital E (phonetic extensions)
    "\U0001d41endorsed",                               # mathematical bold small e
    "ℯndorsed",                                   # script small e (letterlike symbols)
])
def test_gate_050_refuses_confusable_spellings(literal: str) -> None:
    assert "confusable-letter-or-combining-mark" in reasons(with_body(literal), "050_no_endorsement_language")


@pytest.mark.parametrize("literal", ["endor‐\nsed by the author", "endor‑ \n sed"])
def test_gate_050_joins_unicode_hyphen_soft_wraps(literal: str) -> None:
    assert "affiliation-or-backing-language" in reasons(with_body(literal), "050_no_endorsement_language")


# ---------------------------------------------------------------- gate 060

@pytest.mark.parametrize(("literal", "reason"), [
    ("&#101;ndorsed", "html-character-reference"),
    ("&ldquo;an excerpt&rdquo;", "html-character-reference"),
    ("&#8220;x&#8221;", "html-character-reference"),
    ("&#x201C;x", "html-character-reference"),
    ("<blockquote>an excerpt</blockquote>", "html-quotation-element"),
    ("see <q>an excerpt</q>", "html-quotation-element"),
    ("<CITE class=x>", "html-quotation-element"),
    ("'a long excerpt copied from a source'", "single-quoted-span-in-literal"),
    ("as written ('one two three four')", "single-quoted-span-in-literal"),
])
def test_gate_060_refuses_quotation_carriers(literal: str, reason: str) -> None:
    assert reason in reasons(with_body(literal), "060_no_quoted_source_text")


@pytest.mark.parametrize("literal", [
    "it's the user's own lab and the author's title",
    "python3 -m pytest -q -k 'not_vacuous or every_gate'",
    "a < b and c > d in prose",
    "R&D, A & B, and AT&T",
    "the <quote> placeholder is not an element",
])
def test_gates_admit_ordinary_prose_after_hardening(literal: str) -> None:
    counts = base.rows(with_body(literal), GATES)
    assert counts == {gate.stem: 0 for gate in GATES}, literal


# ---------------------------------------------------------------- gate 070

def test_gate_070_refuses_a_second_status_beside_proposal_draft() -> None:
    graph = base.case_graph()
    graph.add((GLC.letter, GLC.letterStatus, Literal("FINAL")))
    assert "letter-with-multiple-statuses" in reasons(graph, "070_letter_author_is_user")


def test_gate_070_refuses_a_language_tagged_twin_status() -> None:
    graph = base.case_graph()
    graph.add((GLC.letter, GLC.letterStatus, Literal("PROPOSAL_DRAFT", lang="en")))
    assert "letter-with-multiple-statuses" in reasons(graph, "070_letter_author_is_user")


def test_gate_070_refuses_letter_fields_on_an_untyped_subject() -> None:
    graph = base.case_graph()
    graph.add((GLC.shadowLetter, GLC.sender, GLC.ghostwriter))
    assert "letter-field-on-untyped-subject" in reasons(graph, "070_letter_author_is_user")


def test_gate_070_refuses_a_subclass_of_letter() -> None:
    graph = base.case_graph()
    graph.add((GLC.ProposalLetter, RDFS.subClassOf, GLC.Letter))
    graph.add((GLC.shadowLetter, RDF.type, GLC.ProposalLetter))
    graph.add((GLC.shadowLetter, GLC.sender, GLC.ghostwriter))
    found = reasons(graph, "070_letter_author_is_user")
    assert {"letter-subclass-declared", "letter-field-on-untyped-subject"} <= found


def test_gate_070_refuses_a_second_user() -> None:
    graph = base.case_graph()
    graph.add((GLC.ghostwriter, RDF.type, GLC.User))
    graph.set((GLC.letter, GLC.sender, GLC.ghostwriter))
    assert "multiple-users-declared" in reasons(graph, "070_letter_author_is_user")


def test_hardened_gates_still_return_zero_rows_on_the_real_packet_and_import_union() -> None:
    graph = base.case_graph()
    for pack in ("evidence-standing-pack", "decision-optionality-pack"):
        graph.parse(base.PACKS / pack / "ontology.ttl", format="turtle")
    assert base.rows(graph, GATES) == {gate.stem: 0 for gate in GATES}


# ---------------------------------------------------------------- runner input

def test_runner_refuses_a_malformed_witness_structurally(tmp_path: Path) -> None:
    witness = tmp_path / "broken.ttl"
    witness.write_text("@prefix glc: <https://ggen.dev/ontology/greene-licensing-case#> .\nglc:x glc:y \"unterminated .\n",
                       encoding="utf-8")
    result = run_runner("--gate", str(GATES[0]), "--witness", str(witness), "--expectation", "pass")
    assert result.returncode == 3, result.stderr
    assert json.loads(result.stderr.strip().splitlines()[-1])["refusal"] == "REFUSED_STRUCTURAL"
    assert "Traceback" not in result.stderr


def test_runner_refuses_a_same_stem_gate_outside_the_pack(tmp_path: Path) -> None:
    foreign = tmp_path / f"{GATES[0].stem}.rq"
    foreign.write_text("SELECT ?s WHERE { ?s ?p ?o }\n", encoding="utf-8")
    witness = PACK / "witnesses" / "fail" / f"{GATES[0].stem}.ttl"
    result = run_runner("--gate", str(foreign), "--witness", str(witness), "--expectation", "fail")
    assert result.returncode == 3, result.stdout + result.stderr
    assert "not one of this pack's gates" in result.stderr


def test_runner_refuses_an_unparseable_gate_structurally(tmp_path: Path) -> None:
    copy = tmp_path / "pack"
    for sub in ("runners", "gates", "ontology", "witnesses"):
        shutil.copytree(PACK / sub, copy / sub)
    shutil.copy2(PACK / "ontology.ttl", copy / "ontology.ttl")
    (copy / "gates" / "080_broken.rq").write_text("SELECT WHERE {\n", encoding="utf-8")
    witness = copy / "witnesses" / "pass" / f"{GATES[0].stem}.ttl"
    result = run_runner("--gate", str(copy / "gates" / f"{GATES[0].stem}.rq"), "--witness", str(witness),
                        "--expectation", "pass", cwd=copy, runner=copy / "runners" / "semantic_runner.py")
    assert result.returncode == 3, result.stdout + result.stderr
    assert json.loads(result.stderr.strip().splitlines()[-1])["refusal"] == "REFUSED_STRUCTURAL"


# ------------------------------------------------ duplicate delivery / reordering

def statement_blocks(path: Path) -> tuple[list[str], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    prefixes = [line for line in lines if line.startswith("@prefix")]
    body = "\n".join(line for line in lines if not line.startswith("@prefix") and not line.startswith("#"))
    blocks = [block.strip() for block in body.split("\n\n") if block.strip()]
    return prefixes, blocks


@pytest.mark.parametrize("gate", GATES, ids=lambda g: g.stem)
@pytest.mark.parametrize("expectation", ["pass", "fail"])
def test_verdict_is_invariant_under_duplicate_delivery_and_reordering(gate: Path, expectation: str,
                                                                      tmp_path: Path) -> None:
    original = PACK / "witnesses" / expectation / f"{gate.stem}.ttl"
    prefixes, blocks = statement_blocks(original)
    shuffled = blocks * 2
    random.Random(26926).shuffle(shuffled)
    variant = tmp_path / f"{gate.stem}.ttl"
    variant.write_text("\n".join(prefixes) + "\n\n" + "\n\n".join(shuffled) + "\n", encoding="utf-8")
    assert isomorphic(Graph().parse(variant), Graph().parse(original))
    verdicts = []
    for witness in (original, variant):
        result = run_runner("--gate", str(gate), "--witness", str(witness), "--expectation", expectation)
        assert result.returncode == 0, result.stderr
        observed = json.loads(result.stdout)
        verdicts.append({k: v for k, v in observed.items() if k != "witness"})
    assert verdicts[0] == verdicts[1]


# ------------------------------------------------ catastrophic backtracking bound

# Measured on the PR head before hardening, the double-quoted-span pattern of
# gate 060 was quadratic: 4.1-12.3 s at 20k characters, so ~9x that at 60k
# pairs (120k characters). After hardening every pattern is near-linear
# (0.9 s at 20k). The bound sits between the two regimes.
ADVERSARIAL_BOUND_SECONDS = 10.0


@pytest.mark.parametrize("literal", [
    '"a' + " a" * 60000,
    " 'a" + " a" * 60000,
    "&a" * 20000,
    "-\n" * 20000,
    "<" * 40000,
], ids=["unterminated-double-quote", "unterminated-single-quote", "ampersand-run", "soft-wrap-run", "angle-run"])
def test_adversarial_literals_are_evaluated_in_bounded_time(literal: str) -> None:
    graph = with_body(literal)
    start = time.perf_counter()
    counts = base.rows(graph, GATES)
    elapsed = time.perf_counter() - start
    assert elapsed < ADVERSARIAL_BOUND_SECONDS, f"{elapsed:.1f}s: a gate regex backtracks catastrophically"
    assert counts == {gate.stem: 0 for gate in GATES}


# ------------------------------------------------ benchmark regression bound

def test_bench_receipt_is_bound_to_the_current_gate_bytes() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["schema"] == "ggen-marketplace.bench/greene-licensing-case-gates/1"
    assert receipt["gate_digests"] == {g.stem: hashlib.sha256(g.read_bytes()).hexdigest() for g in GATES}
    assert set(receipt["gates"]) == {g.stem for g in GATES}
    assert all(entry["rows"] == [0] for entry in receipt["gates"].values())
    assert all(all(v == 0 for v in entry["rows"].values()) for entry in receipt["adversarial"].values())
    assert receipt["regression_bound"]["factor"] >= 1


def test_gate_evaluation_stays_within_the_bench_regression_bound() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    bound = receipt["regression_bound"]
    result = subprocess.run([sys.executable, str(BENCH), "--repeats", "3"], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    now = json.loads(result.stdout)
    assert now["gate_digests"] == receipt["gate_digests"]
    for stem, recorded in receipt["gates"].items():
        limit = max(recorded["p50_seconds"] * bound["factor"], bound["floor_seconds"])
        assert now["gates"][stem]["p50_seconds"] <= limit, (stem, now["gates"][stem], limit)
    for name, recorded in receipt["adversarial"].items():
        limit = max(recorded["total_seconds"] * bound["factor"], bound["floor_seconds"])
        assert now["adversarial"][name]["total_seconds"] <= limit, (name, now["adversarial"][name], limit)
