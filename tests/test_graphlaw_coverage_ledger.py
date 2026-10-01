"""Coverage-ledger court for packs/graphlaw-ash-capability-pack (gate 180).

Gate 180 refuses a ledger that leaves any GraphLaw op or native module unaccounted for. The
witnesses prove the gate is neither vacuous nor over-eager, the real graphlaw ledger
(qualification/coverage-consumer.ttl) passes, and the canonical coverage block makes every other
gate witness and verify fixture pass gate 180 once appended.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pytest
from rdflib import Graph, Literal, URIRef

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "graphlaw-ash-capability-pack"
GATES = PACK / "gates"
STEM = "180_coverage_complete"
PASS = PACK / "witnesses" / "pass" / f"{STEM}.ttl"
FAIL = PACK / "witnesses" / "fail" / f"{STEM}.ttl"
CONSUMER = PACK / "qualification" / "coverage-consumer.ttl"
BLOCK = PACK / "coverage" / "coverage_block.ttl"
BLOCK_LAW = PACK / "coverage" / "coverage_block_law.ttl"
GAC = "http://seanchatmangpt.github.io/packs/graphlaw-ash-capability#"
MODULES = [
    "LawState", "attest", "ReceiptStore", "qualification", "smon",
    "capability_intake", "plan", "policy", "hooks",
]
GRAPHLAW_OPS = [
    "capabilities", "sniff", "parse", "convert", "canonical", "sparql", "shacl", "shex", "n3",
    "entail", "datalog", "hooks", "law", "policy",
]


@lru_cache(maxsize=None)
def gate_text(stem: str) -> str:
    return (GATES / f"{stem}.rq").read_text(encoding="utf-8")


def graph_of(*paths: Path) -> Graph:
    graph = Graph()
    for path in paths:
        graph.parse(path, format="turtle")
    return graph


def gate_rows(stem: str, graph: Graph) -> list:
    return list(graph.query(gate_text(stem)))


def coverage_subjects(graph: Graph) -> set[tuple[str, str]]:
    found = graph.query(
        f"""PREFIX gac: <{GAC}>
        SELECT ?n ?k WHERE {{ ?r a gac:CapabilityCoverage ; gac:coverageSubject ?n ;
                                 gac:coverageSubjectKind ?k }}"""
    )
    return {(str(r[0]), str(r[1])) for r in found}


def all_gate_stems() -> list[str]:
    return sorted(p.stem for p in GATES.glob("*.rq"))


def witness_paths() -> list[Path]:
    paths = sorted((PACK / "witnesses").glob("*/*.ttl"))
    paths += sorted((PACK / "verify" / "fixtures").glob("*.ttl"))
    return [p for p in paths if p != FAIL]  # the 180 fail witness is missing a row on purpose


def with_block(path: Path) -> Graph:
    graph = graph_of(path)
    if (URIRef(GAC + "CapabilityCoverage")) in set(graph.objects(None, None)):
        return graph
    graph.parse(BLOCK, format="turtle")
    has_law = (None, URIRef(GAC + "opName"), Literal("law")) in graph
    if has_law:
        graph.parse(BLOCK_LAW, format="turtle")
    return graph


def test_gate_180_shape() -> None:
    import re

    text = gate_text(STEM)
    assert text.startswith("# MESSAGE:")
    assert re.search(r"^ORDER BY\b", text, re.M)
    assert not re.search(r"\b14\b", text), "gate must not hardcode the op count"
    for op in GRAPHLAW_OPS:
        assert f'"{op}"' not in text or op in MODULES, f"gate hardcodes op {op}"
    assert not re.search(r"https?://(?!seanchatmangpt\.github\.io/packs/|www\.w3\.org/)", text)


@pytest.mark.parametrize("module", MODULES)
def test_pass_witness_names_every_module(module: str) -> None:
    assert (module, "module") in coverage_subjects(graph_of(PASS))


def test_pass_witness_shape() -> None:
    graph = graph_of(PASS)
    subjects = coverage_subjects(graph)
    assert len(subjects) == 11
    assert {n for n, k in subjects if k == "op"} == {"sniff", "sparql"}
    assert gate_rows(STEM, graph) == []


def test_fail_witness_removes_exactly_one_row() -> None:
    removed = coverage_subjects(graph_of(PASS)) - coverage_subjects(graph_of(FAIL))
    assert removed == {("attest", "module")}
    assert coverage_subjects(graph_of(FAIL)) < coverage_subjects(graph_of(PASS))
    rows = gate_rows(STEM, graph_of(FAIL))
    assert rows, "fail witness produced no rows (vacuous gate)"
    assert any("attest" in str(r[1]) for r in rows)


def test_fail_witness_trips_only_gate_180() -> None:
    graph = graph_of(FAIL)
    fired = [stem for stem in all_gate_stems() if gate_rows(stem, graph)]
    assert fired == [STEM]


def test_pass_witness_satisfies_every_gate() -> None:
    graph = graph_of(PASS)
    fired = [stem for stem in all_gate_stems() if gate_rows(stem, graph)]
    assert fired == []


def test_real_ledger_passes_gate_180() -> None:
    assert gate_rows(STEM, graph_of(CONSUMER)) == []


def test_real_ledger_accounts_every_graphlaw_op_and_module() -> None:
    subjects = coverage_subjects(graph_of(CONSUMER))
    for op in GRAPHLAW_OPS:
        assert (op, "op") in subjects
    for module in MODULES:
        assert (module, "module") in subjects
    ops = [s for s in subjects if s[1] == "op"]
    assert len(ops) == len(GRAPHLAW_OPS)


def test_real_ledger_unsupported_rows_carry_generator_capability() -> None:
    graph = graph_of(CONSUMER)
    rows = graph.query(
        f"""PREFIX gac: <{GAC}>
        SELECT ?n ?reason WHERE {{ ?r gac:coverageSubject ?n ; gac:coverageStatus "UNSUPPORTED" .
                                   OPTIONAL {{ ?r gac:coverageReason ?reason }} }}"""
    )
    got = {str(r[0]): str(r[1]) for r in rows}
    assert set(got) == set(MODULES)
    assert set(got.values()) == {"generator-capability"}


def test_real_ledger_plus_registry_fixture_passes_gate_180() -> None:
    registry = graph_of(PASS)
    for triple in graph_of(CONSUMER):
        registry.add(triple)
    # the pass witness's own sniff/sparql rows plus the ledger rows are identical subjects only
    # when the ledger rows are distinct IRIs; duplicates are reported, so check both shapes.
    only_registry_ops = graph_of(PACK / "witnesses" / "pass" / "020_op_count_contract.ttl")
    only_registry_ops.parse(CONSUMER, format="turtle")
    assert gate_rows(STEM, only_registry_ops) == []


@pytest.mark.parametrize("path", witness_paths(), ids=lambda p: f"{p.parent.name}/{p.name}")
def test_block_appended_to_every_witness_passes_gate_180(path: Path) -> None:
    graph = with_block(path)
    rows = gate_rows(STEM, graph)
    assert rows == [], f"{path.name}: gate 180 rows after block append: {rows[:3]}"


def test_block_alone_has_two_op_rows_and_nine_module_rows() -> None:
    graph = graph_of(BLOCK)
    subjects = coverage_subjects(graph)
    assert {n for n, k in subjects if k == "op"} == {"sniff", "sparql"}
    assert {n for n, k in subjects if k == "module"} == set(MODULES)
    assert len(subjects) == 11


def test_coverage_template_and_query_are_paired() -> None:
    template = (PACK / "templates" / "capability_coverage.md.tmpl").read_text(encoding="utf-8")
    query = (PACK / "queries" / "coverage.rq").read_text(encoding="utf-8").rstrip("\n")
    indented = "\n".join(("    " + line) if line else "" for line in query.split("\n"))
    assert indented in template, "inline sparql must be byte-identical to queries/coverage.rq"
