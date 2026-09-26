"""Hardening court for packs/strategic-doctrine-pack (round 2).

Chicago style: the real Turtle graphs parsed by rdflib, the real SPARQL
gates, the real semantic runner and catalog projector as subprocesses, and
the real benchmark module. Assertions are on returned state (gate rows,
reasons, exit codes, stdout bytes, recorded timings). Nothing is faked.

Each test in the "open court findings" block reproduces a defect that was
ADMITTED on c0f27e5b (gate 050 blind to side nodes, multi-node splits and
IRI text; gate 030 admitting two operators on one step; the runner crashing
with a traceback instead of a typed structural refusal) and is now refused.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "strategic-doctrine-pack"
RUNNER = PACK / "runners" / "semantic_runner.py"
SD = Namespace("https://ggen.dev/ontology/strategic-doctrine#")
GATES = sorted((PACK / "gates").glob("*.rq"))
GRAPH_FILES = ("ontology.ttl", "ontology/world-model.ttl", "ontology/doctrine-33.ttl")

sys.path.insert(0, str(PACK / "benchmarks"))
import bench_gates  # noqa: E402  (real module under test, not a double)


def load(*relative: str) -> Graph:
    graph = Graph()
    for item in relative:
        graph.parse(PACK / item, format="turtle")
    return graph


def fired(graph: Graph) -> dict[str, int]:
    rows = {gate.stem: len(list(graph.query(gate.read_text(encoding="utf-8")))) for gate in GATES}
    return {stem: count for stem, count in rows.items() if count}


def reasons(graph: Graph, stem: str) -> list[str]:
    query = (PACK / "gates" / f"{stem}.rq").read_text(encoding="utf-8")
    return sorted(str(row.reason) for row in graph.query(query))


def run_runner(gate: Path, witness: Path, expectation: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(RUNNER), "--gate", str(gate), "--witness", str(witness),
                           "--expectation", expectation], capture_output=True, text=True, check=False)


# --- open court findings: gate 030 ---------------------------------------


@pytest.mark.parametrize("typed", [False, True], ids=["untyped-step", "typed-step"])
def test_step_with_two_primitive_operators_is_refused(typed: bool) -> None:
    graph = load(*GRAPH_FILES)
    step = URIRef("urn:example:two-operator-step") if not typed else SD["strategy-11-step-1"]
    if not typed:
        # Replace step-1 with an untyped twin (same order and operator).
        original = SD["strategy-11-step-1"]
        for predicate, obj in list(graph.predicate_objects(original)):
            if predicate != RDF.type:
                graph.add((step, predicate, obj))
        graph.remove((SD["strategy-11"], SD.composedOf, original))
        graph.remove((original, None, None))
        graph.add((SD["strategy-11"], SD.composedOf, step))
    existing = graph.value(step, SD.operator)
    second = SD.probe if existing != SD.probe else SD.shape
    graph.add((step, SD.operator, second))
    assert fired(graph) == {"030_composition_known_primitive": 1}
    assert reasons(graph, "030_composition_known_primitive") == ["step-with-multiple-operators"]


def test_single_operator_steps_do_not_fire_the_multiple_operator_branch() -> None:
    assert "step-with-multiple-operators" not in reasons(load(*GRAPH_FILES), "030_composition_known_primitive")


# --- open court findings: gate 050 side nodes -----------------------------


@pytest.mark.parametrize("node,kind", [
    (SD["nonclaim-licensing"], None),
    (SD["work-33-strategies"], None),
    (URIRef("urn:example:market-side"), SD.Market),
    (URIRef("urn:example:untyped-side"), None),
])
def test_long_literal_on_a_side_node_is_refused(node: URIRef, kind: URIRef | None) -> None:
    graph = load(*GRAPH_FILES)
    if kind is not None:
        graph.add((node, RDF.type, kind))
    graph.add((node, SD.note, Literal("s" * 301)))
    assert "literal-over-300-chars-on-any-node" in reasons(graph, "050_no_excerpt")
    assert set(fired(graph)) == {"050_no_excerpt"}


def test_side_node_literal_at_the_300_character_cap_is_admitted() -> None:
    graph = load(*GRAPH_FILES)
    graph.add((URIRef("urn:example:untyped-side"), SD.note, Literal("s" * 300)))
    assert fired(graph) == {}


def test_excerpt_split_across_short_literals_on_one_side_node_is_refused() -> None:
    graph = load(*GRAPH_FILES)
    side = URIRef("urn:example:untyped-side")
    for index in range(5):
        graph.add((side, SD.note, Literal(f"{index}" + "k" * 89)))
    assert reasons(graph, "050_no_excerpt") == ["literals-over-400-chars-total-on-any-node"]


def test_nonclaim_prose_as_shipped_stays_under_the_side_node_budget() -> None:
    # Guards the budget choice: the pack's own longest side literal must not
    # be the thing the new branch refuses.
    graph = load("ontology.ttl")
    lengths = [len(str(o)) for o in graph.objects(SD["nonclaim-licensing"], None) if isinstance(o, Literal)]
    assert max(lengths) <= 300 and sum(lengths) <= 400


# --- open court findings: gate 050 multi-node split -----------------------


def test_excerpt_split_across_one_strategy_closure_is_refused() -> None:
    graph = load(*GRAPH_FILES)
    # Each objective node stays under every per-node cap (55 < 60, < 120 total),
    # but together they carry an excerpt past the strategy-closure budget.
    for index in range(5):
        objective = URIRef(f"urn:example:objective-{index}")
        graph.add((SD["strategy-11"], SD.servesObjective, objective))
        graph.add((objective, RDF.type, SD.StrategicObjective))
        graph.add((objective, RDFS.label, Literal(f"{index}" + "o" * 54)))
    assert "literals-over-400-chars-total-across-strategy-closure" in reasons(graph, "050_no_excerpt")
    rows = list(graph.query((PACK / "gates" / "050_no_excerpt.rq").read_text(encoding="utf-8")))
    assert {str(row.subject) for row in rows} == {str(SD["strategy-11"])}


def test_shipped_strategy_closures_stay_under_the_budget() -> None:
    graph = load(*GRAPH_FILES, "fixtures/entrant-world.ttl")
    assert "literals-over-400-chars-total-across-strategy-closure" not in reasons(graph, "050_no_excerpt")


# --- open court findings: gate 050 IRI text channel ----------------------


def test_text_carried_in_an_iri_local_name_is_refused() -> None:
    graph = load(*GRAPH_FILES)
    graph.add((SD["strategy-11"], SD.counteredBy, URIRef("urn:example:" + "a" * 61)))
    assert reasons(graph, "050_no_excerpt") == ["iri-local-name-over-60-chars"]


def test_iri_local_name_at_60_characters_is_admitted() -> None:
    graph = load(*GRAPH_FILES)
    graph.add((SD["strategy-11"], SD.counteredBy, URIRef("urn:example:" + "a" * 60)))
    assert "iri-local-name-over-60-chars" not in reasons(graph, "050_no_excerpt")


def test_text_split_into_short_iri_path_segments_is_refused() -> None:
    graph = load(*GRAPH_FILES)
    long_iri = URIRef("https://example.org/" + "/".join(["word"] * 40))
    graph.add((long_iri, SD.note, Literal("x")))
    assert "iri-over-160-chars" in reasons(graph, "050_no_excerpt")


# --- runner: malformed input, unknown gate, replay, duplicates, reordering --


def test_malformed_witness_is_a_typed_structural_refusal(tmp_path: Path) -> None:
    witness = tmp_path / "broken.ttl"
    witness.write_text("@prefix sd: <https://ggen.dev/ontology/strategic-doctrine#> .\nsd:a sd:b \"unterminated .\n",
                       encoding="utf-8")
    for expectation in ("pass", "fail"):
        run = run_runner(GATES[0], witness, expectation)
        assert run.returncode == 3, run.stderr
        assert json.loads(run.stderr.strip())["refusal"] == "REFUSED_STRUCTURAL"
        assert "Traceback" not in run.stderr


def test_gate_outside_the_pack_with_a_matching_stem_is_refused(tmp_path: Path) -> None:
    foreign = tmp_path / GATES[0].name
    foreign.write_text("SELECT ?x WHERE { ?x ?p ?o }\n", encoding="utf-8")
    run = run_runner(foreign, PACK / "witnesses" / "fail" / f"{GATES[0].stem}.ttl", "fail")
    assert run.returncode == 3
    assert json.loads(run.stderr.strip())["refusal"] == "REFUSED_STRUCTURAL"


def test_missing_witness_is_a_structural_refusal(tmp_path: Path) -> None:
    run = run_runner(GATES[0], tmp_path / "absent.ttl", "pass")
    assert run.returncode == 3


@pytest.mark.parametrize("gate", GATES, ids=lambda gate: gate.stem)
def test_runner_verdict_replays_byte_identically(gate: Path) -> None:
    witness = PACK / "witnesses" / "fail" / f"{gate.stem}.ttl"
    first = run_runner(gate, witness, "fail")
    second = run_runner(gate, witness, "fail")
    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout


@pytest.mark.parametrize("gate", GATES, ids=lambda gate: gate.stem)
def test_duplicate_delivery_and_reordering_do_not_change_the_verdict(gate: Path, tmp_path: Path) -> None:
    for kind in ("pass", "fail"):
        source = PACK / "witnesses" / kind / f"{gate.stem}.ttl"
        graph = Graph()
        graph.parse(source, format="turtle")
        lines = sorted(line for line in graph.serialize(format="nt").splitlines() if line.strip())
        reordered = tmp_path / f"{kind}-reordered.nt.ttl"
        reordered.write_text("\n".join(reversed(lines)) + "\n", encoding="utf-8")
        duplicated = tmp_path / f"{kind}-duplicated.nt.ttl"
        duplicated.write_text("\n".join(lines + lines) + "\n", encoding="utf-8")
        baseline = run_runner(gate, source, kind)
        assert baseline.returncode == 0, baseline.stderr
        for variant in (reordered, duplicated):
            run = run_runner(gate, variant, kind)
            assert run.returncode == 0, run.stderr
            observed = json.loads(run.stdout)
            expected = json.loads(baseline.stdout)
            observed.pop("witness"), expected.pop("witness")
            assert observed == expected


# --- stale subject: the catalog projection refuses a graph edit ------------


def test_catalog_projection_detects_a_stale_catalog(tmp_path: Path) -> None:
    copy = tmp_path / "strategic-doctrine-pack"
    shutil.copytree(PACK, copy, ignore=shutil.ignore_patterns("__pycache__"))
    doctrine = copy / "ontology" / "doctrine-33.ttl"
    text = doctrine.read_text(encoding="utf-8")
    graph = load("ontology/doctrine-33.ttl")
    title = str(graph.value(SD["strategy-11"], SD.shortTitle))
    assert text.count(f'"{title}"') == 1
    doctrine.write_text(text.replace(f'"{title}"', '"Edited own title"'), encoding="utf-8")
    check = subprocess.run([sys.executable, str(copy / "scripts" / "project_catalog.py"), "--check"],
                           capture_output=True, text=True, check=False)
    assert check.returncode == 1, check.stdout + check.stderr


# --- benchmark: recorded numbers and regression bound ----------------------


def test_synthetic_scaled_doctrine_is_admitted_by_every_gate() -> None:
    graph = bench_gates.synthetic_graph(64)
    assert fired(graph) == {}


def test_gate_latency_stays_within_the_recorded_regression_bound() -> None:
    receipt = json.loads((PACK / "benchmarks" / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["schema"] == "ggen.strategic-doctrine.gate-bench/1"
    assert receipt["authority"] == "NONE"
    bound = receipt["regression_bound"]
    observed = bench_gates.measure(bench_gates.doctrine_graph(), repeats=1)
    for stem, recorded in receipt["doctrine"]["median_seconds"].items():
        ceiling = max(recorded * bound["factor"], bound["floor_seconds"])
        assert observed["median_seconds"][stem] <= ceiling, (stem, observed["median_seconds"][stem], ceiling)
    assert observed["rows"] == {gate.stem: 0 for gate in GATES}
    # Scaling: 4x the strategies may cost at most the recorded growth bound.
    small = bench_gates.measure(bench_gates.synthetic_graph(16), repeats=1)["total_seconds"]
    large = bench_gates.measure(bench_gates.synthetic_graph(64), repeats=1)["total_seconds"]
    assert large <= max(small * bound["scale_4x_factor"], bound["floor_seconds"]), (small, large)
