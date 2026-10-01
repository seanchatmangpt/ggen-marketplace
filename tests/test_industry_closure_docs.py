#!/usr/bin/env python3
"""Code-coverage court for the six industry-closure documentation pages.

Chicago style: the collaborators are the real docs, the real pack sources
(ontologies, gates, ggen.toml), the real ``docs/book.ttl`` and
``docs/SUMMARY.md``. Nothing is mocked.

What this court prevents, without a generator script: documentation drift in
both directions. Every ``REFUSED:*`` code, ontology term, gate stem, generated
path and notation that a gate or ontology declares must appear in the matching
reference page, and every such token a page mentions must exist in source. It
also executes the tutorial's own code blocks, so the walkthrough cannot rot.

Scope limit: this proves correspondence between prose and source. It does not
prove the prose is a good explanation, nor any runtime behaviour beyond the
rdflib courts the tutorial itself runs.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
from rdflib import Graph, Namespace, RDF
from rdflib.term import URIRef

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PACKS = ROOT / "packs"

IC_PACK = PACKS / "industry-closure-pack"
EOM_PACK = PACKS / "enterprise-operating-model-pack"
LND_PACK = PACKS / "industry-closure-retail-lending-profile-pack"
EA_ONTOLOGY = PACKS / "enterprise-architecture-pack" / "ontology.ttl"

IC_NS = "https://seanchatmangpt.github.io/packs/industry-closure-pack#"
EOM_NS = "https://seanchatmangpt.github.io/packs/enterprise-operating-model-pack#"
EA_NS = "https://chatman.ai/ontology/enterprise-architecture#"

TUTORIAL = DOCS / "tutorials" / "generate-an-industry-closure.md"
HOWTO_ADD = DOCS / "how-to" / "add-an-industry-to-closure.md"
HOWTO_TRIAGE = DOCS / "how-to" / "triage-an-industry-closure-residual.md"
REF_IC = DOCS / "reference" / "industry-closure-contract.md"
REF_EOM = DOCS / "reference" / "enterprise-operating-model-contract.md"
EXPLANATION = DOCS / "explanation" / "industry-closure-as-architecture-strategy.md"

PAGES = [TUTORIAL, HOWTO_ADD, HOWTO_TRIAGE, REF_IC, REF_EOM, EXPLANATION]
QUADRANTS = {"tutorials", "how-to", "reference", "explanation"}

REFUSED_LITERAL = re.compile(r'"(REFUSED:[A-Z0-9_]+)"')
DOC_CODE = re.compile(r"REFUSED:((?:IC|EOM|LND)_[A-Z0-9_]+)")
PREFIXED = {
    "ic": re.compile(r"(?<![A-Za-z0-9_])ic:([A-Za-z][A-Za-z0-9_]*)"),
    "eom": re.compile(r"(?<![A-Za-z0-9_])eom:([A-Za-z][A-Za-z0-9_]*)"),
    "ea": re.compile(r"(?<![A-Za-z0-9_])ea:([A-Za-z][A-Za-z0-9_]*)"),
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def gate_codes(pack: Path) -> set[str]:
    codes: set[str] = set()
    for gate in sorted((pack / "gates").glob("*.rq")):
        codes |= {c[len("REFUSED:"):] for c in REFUSED_LITERAL.findall(read(gate))}
    return codes


def declared_terms(ontology: Path, namespace: str) -> dict[str, str]:
    """Local name to kind for every typed subject in the namespace."""
    graph = Graph()
    graph.parse(ontology, format="turtle")
    terms: dict[str, str] = {}
    for subject, _, kind in graph.triples((None, RDF.type, None)):
        if isinstance(subject, URIRef) and str(subject).startswith(namespace):
            terms[str(subject)[len(namespace):]] = str(kind)
    return terms


def mentioned(prefix: str, text: str) -> set[str]:
    return set(PREFIXED[prefix].findall(text))


@pytest.fixture(scope="module")
def ic_terms() -> dict[str, str]:
    return declared_terms(IC_PACK / "ontology.ttl", IC_NS)


@pytest.fixture(scope="module")
def eom_terms() -> dict[str, str]:
    return declared_terms(EOM_PACK / "ontology.ttl", EOM_NS)


@pytest.fixture(scope="module")
def ea_names() -> set[str]:
    graph = Graph()
    graph.parse(EA_ONTOLOGY, format="turtle")
    names: set[str] = set()
    for triple in graph:
        for node in triple:
            if isinstance(node, URIRef) and str(node).startswith(EA_NS):
                names.add(str(node)[len(EA_NS):])
    return names


# ---------------------------------------------------------------------------
# The six pages exist and cover all four Diataxis quadrants
# ---------------------------------------------------------------------------

def test_six_pages_exist_and_are_nonempty() -> None:
    for page in PAGES:
        assert page.is_file(), f"missing docs page: {page.relative_to(ROOT)}"
        assert len(read(page).strip()) > 500, f"docs page is a stub: {page.relative_to(ROOT)}"


def test_every_quadrant_is_represented() -> None:
    present = {page.parent.name for page in PAGES}
    assert present == QUADRANTS, f"quadrants present {sorted(present)}, required {sorted(QUADRANTS)}"
    assert len(PAGES) == 6


def test_each_page_has_a_single_h1_and_names_its_quadrant_purpose() -> None:
    for page in PAGES:
        h1 = [l for l in read(page).splitlines() if l.startswith("# ")]
        assert len(h1) == 1, f"{page.name}: expected exactly one H1, found {h1}"


# ---------------------------------------------------------------------------
# REFUSED codes: gates to docs and docs to gates
# ---------------------------------------------------------------------------

def test_ic_reference_lists_every_ic_code_exactly_as_the_gates_declare() -> None:
    declared = {c for c in gate_codes(IC_PACK) if c.startswith("IC_")}
    assert declared, "no IC_ codes parsed from gates; the court is vacuous"
    documented = {c for c in DOC_CODE.findall(read(REF_IC)) if c.startswith("IC_")}
    assert declared - documented == set(), f"IC codes missing from reference: {sorted(declared - documented)}"
    assert documented - declared == set(), f"IC codes in reference but in no gate: {sorted(documented - declared)}"


def test_eom_reference_lists_every_eom_code_exactly_as_the_gates_declare() -> None:
    declared = gate_codes(EOM_PACK)
    assert declared and all(c.startswith("EOM_") for c in declared)
    documented = set(DOC_CODE.findall(read(REF_EOM)))
    assert declared - documented == set(), f"EOM codes missing from reference: {sorted(declared - documented)}"
    assert documented - declared == set(), f"EOM codes in reference but in no gate: {sorted(documented - declared)}"


def test_profile_codes_are_documented_in_the_ic_reference() -> None:
    declared = gate_codes(LND_PACK)
    assert declared and all(c.startswith("LND_") for c in declared)
    documented = {c for c in DOC_CODE.findall(read(REF_IC)) if c.startswith("LND_")}
    assert declared == documented, f"LND codes declared {sorted(declared)} documented {sorted(documented)}"


def test_triage_failure_catalogue_covers_every_ic_and_profile_code() -> None:
    declared = {c for c in gate_codes(IC_PACK) | gate_codes(LND_PACK)}
    documented = set(DOC_CODE.findall(read(HOWTO_TRIAGE)))
    assert declared - documented == set(), f"codes without a repair: {sorted(declared - documented)}"
    assert documented - declared == set(), f"repairs for codes in no gate: {sorted(documented - declared)}"


def test_no_page_mentions_a_code_that_no_gate_declares() -> None:
    declared = gate_codes(IC_PACK) | gate_codes(EOM_PACK) | gate_codes(LND_PACK)
    for page in PAGES:
        phantom = set(DOC_CODE.findall(read(page))) - declared
        assert phantom == set(), f"{page.name} mentions undeclared codes: {sorted(phantom)}"


def test_reference_tables_put_each_code_next_to_its_gate_stem() -> None:
    """A code row must sit under the gate that declares it, not merely appear."""
    for ref, pack, prefix in ((REF_IC, IC_PACK, "IC_"), (REF_EOM, EOM_PACK, "EOM_")):
        lines = read(ref).splitlines()
        for gate in sorted((pack / "gates").glob("*.rq")):
            expected = {c[len("REFUSED:"):] for c in REFUSED_LITERAL.findall(read(gate))}
            stem_rows = [i for i, l in enumerate(lines) if f"`{gate.name}`" in l and l.startswith("|")]
            assert stem_rows, f"{ref.name}: gate {gate.name} is not named in a table row"
            start = stem_rows[0]
            found: set[str] = set()
            for line in lines[start:]:
                if not line.startswith("|"):
                    break
                if line is not lines[start] and re.match(r"\|\s*`\d{3}_", line):
                    break
                found |= set(DOC_CODE.findall(line))
            assert found == {c for c in expected if c.startswith(prefix)}, (
                f"{ref.name}: rows under {gate.name} list {sorted(found)}, gate declares {sorted(expected)}"
            )


# ---------------------------------------------------------------------------
# Ontology terms: source to docs and docs to source
# ---------------------------------------------------------------------------

def test_every_ic_term_a_page_mentions_exists_in_the_ontology(ic_terms: dict[str, str]) -> None:
    for page in PAGES:
        unknown = mentioned("ic", read(page)) - set(ic_terms)
        assert unknown == set(), f"{page.name} mentions undeclared ic: terms {sorted(unknown)}"


def test_every_eom_term_a_page_mentions_exists_in_the_ontology(eom_terms: dict[str, str]) -> None:
    for page in PAGES:
        unknown = mentioned("eom", read(page)) - set(eom_terms)
        assert unknown == set(), f"{page.name} mentions undeclared eom: terms {sorted(unknown)}"


def test_every_ea_term_a_page_mentions_exists_in_the_ea_ontology(ea_names: set[str]) -> None:
    assert ea_names, "enterprise-architecture-pack ontology yielded no ea: names"
    for page in PAGES:
        unknown = mentioned("ea", read(page)) - ea_names
        assert unknown == set(), f"{page.name} mentions ea: terms absent from the owning ontology {sorted(unknown)}"


def test_ic_reference_documents_every_declared_ic_term(ic_terms: dict[str, str]) -> None:
    assert len(ic_terms) > 50, "ic ontology parse looks vacuous"
    missing = set(ic_terms) - mentioned("ic", read(REF_IC))
    assert missing == set(), f"ic terms declared but absent from the reference: {sorted(missing)}"


def test_eom_reference_documents_every_declared_eom_term(eom_terms: dict[str, str]) -> None:
    assert len(eom_terms) > 50, "eom ontology parse looks vacuous"
    missing = set(eom_terms) - mentioned("eom", read(REF_EOM))
    assert missing == set(), f"eom terms declared but absent from the reference: {sorted(missing)}"


def test_ic_reference_declares_property_domains_not_just_names() -> None:
    text = read(REF_IC)
    graph = Graph()
    graph.parse(IC_PACK / "ontology.ttl", format="turtle")
    rdfs_domain = URIRef("http://www.w3.org/2000/01/rdf-schema#domain")
    for prop, domain in graph.subject_objects(rdfs_domain):
        if not str(prop).startswith(IC_NS) or not str(domain).startswith(IC_NS):
            continue
        row = next((l for l in text.splitlines() if l.startswith(f"| `ic:{str(prop)[len(IC_NS):]}`")), None)
        assert row is not None, f"no table row for ic:{str(prop)[len(IC_NS):]}"
        assert f"`ic:{str(domain)[len(IC_NS):]}`" in row, f"row for {prop} omits its domain {domain}"


# ---------------------------------------------------------------------------
# Routing, notation, gates and generated paths
# ---------------------------------------------------------------------------

def test_deficit_class_routing_row_matches_ontology_data() -> None:
    graph = Graph()
    graph.parse(IC_PACK / "ontology.ttl", format="turtle")
    ic = Namespace(IC_NS)
    classes = list(graph.subjects(RDF.type, ic.DeficitClass))
    assert len(classes) == 7, f"expected seven deficit classes, found {len(classes)}"
    lines = read(REF_IC).splitlines()
    for cls in classes:
        name = str(cls)[len(IC_NS):]
        target = str(graph.value(cls, ic.routesTo))[len(IC_NS):]
        delta = str(graph.value(cls, ic.deltaCode))
        rows = [l for l in lines if l.startswith(f"| `ic:{name}` |") and f"`ic:{target}`" in l]
        assert rows, f"routing row for {name} -> {target} not found in reference"
        assert any(f"`{delta}`" in l for l in rows), f"delta code {delta} for {name} not on its routing row"


def test_class_precedence_table_follows_the_classifier() -> None:
    source = read(IC_PACK / "queries" / "10-residual.rq")
    core = re.search(r"BEGIN R_CORE(.*?)END R_CORE", source, re.S)
    assert core, "R_CORE block missing from the residual query"
    order = re.findall(r"ic:(DEFICIT_[A-Z]+)", core.group(1))
    seen: list[str] = []
    for name in order:
        if name not in seen:
            seen.append(name)
    assert len(seen) == 7, f"classifier order {seen}"
    text = read(REF_IC)
    table = [l for l in text.splitlines() if re.match(r"\| \d \| `ic:DEFICIT_", l)]
    documented = [re.search(r"`ic:(DEFICIT_[A-Z]+)`", l).group(1) for l in table]
    assert documented == seen, f"documented precedence {documented} differs from classifier {seen}"


def test_references_name_every_gate_file() -> None:
    for ref, pack in ((REF_IC, IC_PACK), (REF_EOM, EOM_PACK)):
        text = read(ref)
        for gate in sorted((pack / "gates").glob("*.rq")):
            assert gate.name in text, f"{ref.name} does not name gate {gate.name}"
    assert (LND_PACK / "gates" / "010_profile_grounding.rq").name in read(REF_IC)


def test_references_name_every_generation_rule_and_output() -> None:
    for ref, pack in ((REF_IC, IC_PACK), (REF_EOM, EOM_PACK)):
        config = tomllib.loads(read(pack / "ggen.toml"))
        text = read(ref)
        rules = config["generation"]["rules"]
        assert rules, f"{pack.name} has no generation rules"
        for rule in rules:
            assert f"`{rule['name']}`" in text, f"{ref.name} omits rule {rule['name']}"
            assert rule["output_file"] in text, f"{ref.name} omits output {rule['output_file']}"
            assert rule["query"]["file"] in text, f"{ref.name} omits query {rule['query']['file']}"


def test_eom_reference_carries_every_notation_join_key(eom_terms: dict[str, str]) -> None:
    graph = Graph()
    graph.parse(EOM_PACK / "ontology.ttl", format="turtle")
    notation = URIRef("http://www.w3.org/2004/02/skos/core#notation")
    keys = {str(o) for o in graph.objects(None, notation)}
    assert len(keys) >= 15, f"expected the OM/MAT/ADM keys, found {sorted(keys)}"
    text = read(REF_EOM)
    missing = {k for k in keys if k not in text}
    assert missing == set(), f"notation join keys absent from reference: {sorted(missing)}"


def test_eom_reference_axes_truth_table_matches_the_ontology() -> None:
    graph = Graph()
    graph.parse(EOM_PACK / "ontology.ttl", format="turtle")
    eom = Namespace(EOM_NS)
    text = read(REF_EOM)
    for model in ("Diversification", "Coordination", "Replication", "Unification"):
        node = eom[model]
        integ = str(graph.value(node, eom.integrationLevel))[len(EOM_NS):]
        stand = str(graph.value(node, eom.standardizationLevel))[len(EOM_NS):]
        row = next((l for l in text.splitlines() if l.startswith(f"| `eom:{model}` | `eom:{integ}` | `eom:{stand}` |")), None)
        assert row is not None, f"truth-table row for {model} ({integ}, {stand}) missing or wrong"


def test_eom_reference_stage_ordinals_match_the_ontology() -> None:
    graph = Graph()
    graph.parse(EOM_PACK / "ontology.ttl", format="turtle")
    eom = Namespace(EOM_NS)
    text = read(REF_EOM)
    stages = list(graph.subjects(RDF.type, eom.MaturityStage))
    assert len(stages) == 4
    for stage in stages:
        name = str(stage)[len(EOM_NS):]
        ordinal = int(graph.value(stage, eom.stageOrdinal))
        row = next((l for l in text.splitlines() if l.startswith(f"| `eom:{name}` |")), None)
        assert row is not None, f"stage row for {name} missing"
        assert f"| {ordinal} |" in row, f"ordinal {ordinal} for {name} missing on its row"


def test_eom_reference_adm_order_matches_precedes() -> None:
    graph = Graph()
    graph.parse(EOM_PACK / "ontology.ttl", format="turtle")
    eom = Namespace(EOM_NS)
    text = read(REF_EOM)
    for phase, successor in graph.subject_objects(eom.precedes):
        a, b = str(phase)[len(EOM_NS):], str(successor)[len(EOM_NS):]
        row = next((l for l in text.splitlines() if l.startswith(f"| `eom:{a}` |")), None)
        assert row is not None and f"`eom:{b}`" in row, f"ADM order row {a} -> {b} missing"


# ---------------------------------------------------------------------------
# Honest standing, authority fence, volatile values
# ---------------------------------------------------------------------------

def test_pages_state_the_honest_standing_without_ggen() -> None:
    for page in (TUTORIAL, REF_IC, REF_EOM, EXPLANATION):
        text = read(page)
        assert "BLOCKED:ggen_binary_unavailable" in text, f"{page.name} omits the honest manufacture standing"
        assert "Level-5" in text, f"{page.name} omits the Level-5 non-claim"


def test_pages_state_the_authority_fence() -> None:
    for page in (REF_IC, REF_EOM, EXPLANATION):
        text = read(page)
        assert "DO" in text and "SELECT" in text and "CONSTRUCT" in text, f"{page.name} omits the authority fence"
        assert re.search(r"no DO|DO is not representable|not representable", text), f"{page.name} omits the DO-unrepresentable statement"
    assert "QUALIFIED is not ALIVE" in read(REF_IC) or "QUALIFIED` is not ALIVE" in read(REF_IC)


# A prose line may mention ALIVE only inside one of these fenced phrasings (word-bounded, same clause): a negation
# or "nothing" that precedes ALIVE, ALIVE followed by requires/needs/only, "only ... ALIVE", or the standing
# vocabulary written as the ladder list. A bare substring such as "no ", "not" inside "another" or "UNKNOWN"
# elsewhere on the line is not a fence.
_ALIVE = r"(?<![\w])ALIVE(?![\w])"
ALIVE_FENCES = (
    re.compile(r"\b(?i:not|never|cannot|nothing|none)\b[^.\n]*" + _ALIVE),
    re.compile(_ALIVE + r"[^.\n]*\b(?i:requires|needs|only)\b"),
    re.compile(r"\b(?i:only)\b[^.\n]*" + _ALIVE),
    re.compile(r"`?UNKNOWN`?,\s*`?PARTIAL_ALIVE`?,\s*`?ALIVE`?"),
)


def alive_line_is_fenced(line: str) -> bool:
    """True when the line has no ALIVE claim, or only a fenced mention of it."""
    if not re.search(_ALIVE, line):
        return True
    return any(fence.search(line) for fence in ALIVE_FENCES)


def test_no_page_asserts_alive_without_a_negation() -> None:
    for page in PAGES:
        for number, line in enumerate(read(page).splitlines(), 1):
            if line.startswith("|"):
                continue  # table rows state gate triggers; prose lines are the claims
            assert alive_line_is_fenced(line), f"{page.name}:{number} mentions ALIVE without a fence: {line.strip()}"


@pytest.mark.parametrize("line", [
    "Every stage is ALIVE, no problem.",
    "Status: ALIVE (UNKNOWN is gone).",
    "ALIVE is another state of the pack.",
    "The pack is ALIVE and nothing else matters.",
    "The ledger is ALIVE; we do not doubt it.",
])
def test_the_alive_lint_rejects_a_claim_that_only_resembles_a_fence(line: str) -> None:
    assert not alive_line_is_fenced(line)


@pytest.mark.parametrize("line", [
    "Nothing here is ALIVE.",
    "`ea:QUALIFIED` is not ALIVE.",
    "Evidence can never support ALIVE for a real capability.",
    "A coverage may be called ALIVE only with independent evidence.",
    "ALIVE requires observed evidence.",
    "The standing ladder is UNKNOWN, PARTIAL_ALIVE, ALIVE, BLOCKED.",
    "Semantic source is `PARTIAL_ALIVE` for the pack.",
])
def test_the_alive_lint_accepts_the_fenced_phrasings(line: str) -> None:
    assert alive_line_is_fenced(line)


def test_pages_hardcode_no_volatile_values() -> None:
    for page in PAGES:
        text = read(page)
        assert not re.search(r"[0-9a-f]{40,}", text), f"{page.name} contains a digest or commit-like value"
        assert not re.search(r"(?<![\w.])2\d\.\d{1,2}\.\d{1,3}(?![\w.])", text), f"{page.name} contains a CalVer-like version"
        assert not re.search(r"ggen\s+v?\d+\.\d+", text, re.I), f"{page.name} hardcodes a ggen version"
        assert not re.search(r"\b\d+\s*(?:s|sec|seconds|ms)\b\s*timeout|timeout\s*[=:]\s*\d+", text, re.I), f"{page.name} hardcodes a timeout"


def test_pages_claim_no_do_authority_in_code_blocks() -> None:
    for page in PAGES:
        for block in re.findall(r"```(?:turtle|python|text|bash)?\n(.*?)```", read(page), re.S):
            assert not re.search(r'authorityClaim\s+"(?!NONE")', block), f"{page.name}: authority claim other than NONE in a code block"
            assert "grantsDoAuthority true" not in block, f"{page.name}: grants DO authority in a code block"


# ---------------------------------------------------------------------------
# Links and navigation
# ---------------------------------------------------------------------------

def test_relative_links_resolve() -> None:
    for page in PAGES:
        for target in re.findall(r"\]\(([^)\s]+)\)", read(page)):
            if re.match(r"[a-z]+:", target) or target.startswith("#"):
                continue
            path = (page.parent / target.split("#")[0]).resolve()
            assert path.exists(), f"{page.name}: broken link {target}"


def test_required_cross_links_are_present() -> None:
    explanation = read(EXPLANATION)
    assert "class-closure-and-consolidation.md" in explanation
    assert "pack-classes.md" in explanation
    assert "consolidate-a-pack-family.md" in explanation
    for page in (TUTORIAL, HOWTO_ADD, HOWTO_TRIAGE, EXPLANATION):
        assert "industry-closure-contract.md" in read(page) or page is EXPLANATION, f"{page.name} does not link the reference"
    for pack in (IC_PACK, EOM_PACK):
        readme = read(pack / "README.md")
        for page in PAGES:
            if page.name in readme:
                assert page.exists()


def test_each_page_has_a_book_entry_and_a_summary_line() -> None:
    """Navigation is lane F's job (docs/book.ttl is the source, SUMMARY.md a projection).

    This test is red until those entries exist: that is the intended signal.
    """
    book = read(DOCS / "book.ttl")
    summary = read(DOCS / "SUMMARY.md")
    for page in PAGES:
        rel = page.relative_to(DOCS).as_posix()
        assert f'mdp:path "{rel}"' in book, f"docs/book.ttl has no entry for {rel}"
        assert f"({rel})" in summary, f"docs/SUMMARY.md has no line for {rel}"


# ---------------------------------------------------------------------------
# The tutorial runs
# ---------------------------------------------------------------------------

def test_tutorial_code_blocks_execute_and_print_what_the_page_claims(tmp_path: Path) -> None:
    text = read(TUTORIAL)
    blocks = re.findall(r"```python\n(.*?)```", text, re.S)
    assert len(blocks) >= 6, "tutorial lost its executable blocks"
    script = tmp_path / "closure_tour.py"
    script.write_text("\n\n".join(blocks), encoding="utf-8")
    run = subprocess.run(
        [sys.executable, str(script)], cwd=ROOT, capture_output=True, text=True, timeout=600
    )
    assert run.returncode == 0, f"tutorial script failed:\n{run.stderr[-2000:]}"
    out = run.stdout
    expected = [
        "stage0-no-abb [('REQ-A--CAP-A', 'DEFICIT_ABB')]",
        "stage1-abb-contract-pending [('REQ-A--CAP-A', 'DEFICIT_CONTRACT')]",
        "stage2-contract-approved-no-sbb [('REQ-A--CAP-A', 'DEFICIT_SBB')]",
        "stage3-sbb-candidate [('REQ-A--CAP-A', 'DEFICIT_QUALIFICATION')]",
        "stage4-sbb-qualified-no-evidence [('REQ-A--CAP-A', 'DEFICIT_EVIDENCE')]",
        "stage5-verified-covered covered",
        "stage6-falsified-stale [('REQ-A--CAP-A', 'DEFICIT_EVIDENCE')]",
        "REFUSED:IC_CONTRACT_APPROVAL_UNATTRIBUTED",
        "REFUSED:IC_FRONTIER_UNRECORDED",
        "030_snapshot_identity pass",
        "040_closure_monotonicity pass",
        "050_coverage_chain pass",
        "055_frontier_recorded pass",
        "REFUSED:IC_CLOSURE_SHRINK",
        "EVIDENCE_NOT_CURRENT",
        "REFUSED:IC_COVERAGE_EVIDENCE_FALSIFIED",
        "REFUSED:IC_EVIDENCE_FALSIFICATION_UNFED",
        "3 requirement rows; 2 skeleton rows",
        "LND-REQ-10 CAP-FUNDING-INSTRUCTION DEFICIT_AUTHORITY BLOCKED",
    ]
    for needle in expected:
        assert needle in out, f"tutorial output lacks {needle!r}\n--- stdout ---\n{out[-3000:]}"


def test_tutorial_python_blocks_make_no_filesystem_writes_in_the_repository() -> None:
    for block in re.findall(r"```python\n(.*?)```", read(TUTORIAL), re.S):
        assert not re.search(r"\.write_text|open\([^)]*['\"]w", block), "tutorial code writes files"
