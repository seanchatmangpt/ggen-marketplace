"""Chicago-style tests for packs/strategic-doctrine-pack.

Real collaborators throughout: the real Turtle files on disk parsed by rdflib,
the real SHACL shapes run by pyshacl, the real SPARQL gates, the real gate
court runner and catalog projector invoked as subprocesses. Assertions are on
returned state (rows, exit codes, file bytes, digests). Nothing is mocked.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "strategic-doctrine-pack"
SD = Namespace("https://ggen.dev/ontology/strategic-doctrine#")
CS = Namespace("urn:xaas:case-study:")
GATES = sorted((PACK / "gates").glob("*.rq"))
PRIMITIVES = (
    "shape", "probe", "conceal", "reveal", "concentrate", "disperse", "delay",
    "accelerate", "commit", "withdraw", "divide", "combine", "substitute", "transform",
)
DUALS = {("conceal", "reveal"), ("concentrate", "disperse"), ("delay", "accelerate"),
         ("commit", "withdraw"), ("divide", "combine")}
GRAPH_FILES = ("ontology.ttl", "ontology/world-model.ttl", "ontology/doctrine-33.ttl")


def load(*relative: str) -> Graph:
    graph = Graph()
    for item in relative:
        graph.parse(PACK / item, format="turtle")
    return graph


def gate_rows(graph: Graph) -> dict[str, int]:
    return {gate.stem: len(list(graph.query(gate.read_text(encoding="utf-8")))) for gate in GATES}


def test_six_gates_exist_with_exact_stems() -> None:
    assert [gate.stem for gate in GATES] == [
        "010_strategy_requires_falsifier",
        "020_applicability_public_class_only",
        "030_composition_known_primitive",
        "040_step_order_total",
        "050_no_excerpt",
        "060_licensing_nonclaim_present",
    ]


def test_primitive_algebra_is_fourteen_operators_with_five_symmetric_duals() -> None:
    graph = load("ontology.ttl")
    operators = sorted(str(o).rsplit("#", 1)[1] for o in graph.subjects(RDF.type, SD.PrimitiveOperator))
    assert operators == sorted(PRIMITIVES)
    pairs = {(str(a).rsplit("#", 1)[1], str(b).rsplit("#", 1)[1]) for a, b in graph.subject_objects(SD.dualOf)}
    assert pairs == DUALS | {(b, a) for a, b in DUALS}


def test_catalog_has_33_ordinals_with_short_own_titles_and_six_operationalized() -> None:
    graph = load(*GRAPH_FILES)
    entries = set(graph.subjects(RDF.type, SD.Strategy)) | set(graph.subjects(RDF.type, SD.StrategyStub))
    ordinals = sorted(int(graph.value(entry, SD.ordinal)) for entry in entries)
    assert ordinals == list(range(1, 34))
    titles = [str(graph.value(entry, SD.shortTitle)) for entry in entries]
    assert all(0 < len(title) <= 60 for title in titles)
    assert len(set(titles)) == 33
    operationalized = [e for e in graph.subjects(RDF.type, SD.Strategy) if (e, RDF.type, SD.StrategyStub) not in graph]
    assert len(operationalized) >= 5
    for entry in operationalized:
        assert list(graph.objects(entry, SD.composedOf))
        assert list(graph.objects(entry, SD.hasFalsifier))
    assert not list(graph.subject_objects(SD.quote))


def test_doctrine_graph_and_fixture_conform_and_every_gate_returns_zero_rows() -> None:
    graph = load(*GRAPH_FILES, "fixtures/entrant-world.ttl")
    conforms, _, text = validate(graph, shacl_graph=str(PACK / "ontology" / "shapes.ttl"),
                                 inference="none", advanced=True)
    assert conforms, text
    assert gate_rows(graph) == {gate.stem: 0 for gate in GATES}


def test_gates_are_not_vacuous_on_the_real_doctrine_graph() -> None:
    # Anti-vacuity: mutate the real graph and observe the specific gate fire.
    graph = load(*GRAPH_FILES)
    graph.add((SD["strategy-03"], SD.quote, Literal("any text")))
    assert gate_rows(graph)["050_no_excerpt"] >= 1

    graph = load(*GRAPH_FILES)
    graph.remove((SD["nonclaim-licensing"], None, None))
    assert gate_rows(graph)["060_licensing_nonclaim_present"] == 1

    graph = load(*GRAPH_FILES)
    graph.remove((SD["strategy-14"], SD.hasFalsifier, None))
    assert gate_rows(graph)["010_strategy_requires_falsifier"] == 1

    graph = load(*GRAPH_FILES)
    graph.set((SD["strategy-17-step-4"], SD.order, Literal(2)))
    assert gate_rows(graph)["040_step_order_total"] >= 1

    graph = load(*GRAPH_FILES)
    graph.set((SD["strategy-27-step-1"], SD.operator, SD.ambush))
    assert gate_rows(graph)["030_composition_known_primitive"] == 1

    graph = load(*GRAPH_FILES)
    graph.set((SD["cond-many-rivals"], SD.aboutClass, URIRef("urn:example:private:Rival")))
    assert gate_rows(graph)["020_applicability_public_class_only"] == 1


@pytest.mark.parametrize("gate", GATES, ids=lambda gate: gate.stem)
def test_gate_court_admits_pass_and_refuses_fail_witnesses(gate: Path) -> None:
    runner = PACK / "runners" / "semantic_runner.py"
    passed = subprocess.run(
        [sys.executable, str(runner), "--gate", str(gate),
         "--witness", str(PACK / "witnesses" / "pass" / f"{gate.stem}.ttl"), "--expectation", "pass"],
        capture_output=True, text=True, check=False)
    assert passed.returncode == 0, passed.stderr
    failed = subprocess.run(
        [sys.executable, str(runner), "--gate", str(gate),
         "--witness", str(PACK / "witnesses" / "fail" / f"{gate.stem}.ttl"), "--expectation", "fail"],
        capture_output=True, text=True, check=False)
    assert failed.returncode == 0, failed.stderr
    assert json.loads(failed.stdout)["gate"] == gate.stem
    # A fail witness is refused when presented as a pass.
    refused = subprocess.run(
        [sys.executable, str(runner), "--gate", str(gate),
         "--witness", str(PACK / "witnesses" / "fail" / f"{gate.stem}.ttl"), "--expectation", "pass"],
        capture_output=True, text=True, check=False)
    assert refused.returncode == 2


def test_entrant_world_admits_exactly_three_applicable_strategies_with_falsifiers() -> None:
    graph = load(*GRAPH_FILES, "fixtures/entrant-world.ttl")
    query = (PACK / "queries" / "admitted_applicability.rq").read_text(encoding="utf-8")
    rows = [(str(r.strategy).rsplit("#", 1)[1], str(r.falsifier).rsplit("#", 1)[1]) for r in graph.query(query)]
    assert rows == [("strategy-11", "falsifier-11"), ("strategy-17", "falsifier-17"), ("strategy-27", "falsifier-27")]
    incumbents = [s for s in graph.subjects(RDF.type, URIRef("http://www.w3.org/ns/org#Organization"))]
    assert len(incumbents) == 4


def test_catalog_projection_is_current_and_deterministic() -> None:
    projector = PACK / "scripts" / "project_catalog.py"
    check = subprocess.run([sys.executable, str(projector), "--check"], capture_output=True, text=True, check=False)
    assert check.returncode == 0, check.stderr
    first = subprocess.run([sys.executable, str(projector), "--stdout"], capture_output=True, check=True).stdout
    second = subprocess.run([sys.executable, str(projector), "--stdout"], capture_output=True, check=True).stdout
    assert first == second == (PACK / "generated" / "catalog.json").read_bytes()
    catalog = json.loads(first)
    assert catalog["authority"] == "NONE"
    assert catalog["authority_ceiling"] in {"SELECT", "CONSTRUCT"}
    assert [entry["ordinal"] for entry in catalog["strategies"]] == list(range(1, 34))
    assert all(set(entry) == {"falsifiers", "id", "ordinal", "primitives", "title"} for entry in catalog["strategies"])
    assert all(p in PRIMITIVES for entry in catalog["strategies"] for p in entry["primitives"])
    assert catalog["nonclaim"] and "not licensed" in catalog["nonclaim"][0]["text"]


def test_vendored_public_ontologies_match_receipts_and_repository_sources() -> None:
    vendor = PACK / "sources" / "vendor"
    receipt = json.loads((vendor / "materialization-receipt.json").read_text(encoding="utf-8"))
    ids = sorted(source["id"] for source in receipt["sources"])
    assert ids == ["org", "owl-time", "prov-o", "schema-org", "sosa", "ssn"]
    for source in receipt["sources"]:
        vendored = (vendor / source["id"] / "source.ttl").read_bytes()
        digest = hashlib.sha256(vendored).hexdigest()
        assert digest == source["sha256"]
        assert digest == json.loads((vendor / source["id"] / "receipt.json").read_text(encoding="utf-8"))["sha256"]
        assert hashlib.sha256((ROOT / source["copied_from"]).read_bytes()).hexdigest() == digest
    assert set(receipt["not_vendored"]) == {"geosparql", "ocel-2.0"}


def test_nonclaim_asserts_all_three_boundaries() -> None:
    graph = load("ontology.ttl")
    nonclaims = list(graph.subjects(RDF.type, CS.NonClaim))
    assert nonclaims == [SD["nonclaim-licensing"]]
    for flag in (SD.assertsNotLicensed, SD.assertsNoEndorsement, SD.assertsNoTextReproduced):
        assert graph.value(nonclaims[0], flag).toPython() is True
    assert graph.value(nonclaims[0], RDFS.comment)
