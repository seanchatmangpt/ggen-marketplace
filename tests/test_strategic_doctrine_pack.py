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


OPERATIONALIZED = ["strategy-11", "strategy-14", "strategy-17", "strategy-22", "strategy-23", "strategy-27"]


def gate_rows(graph: Graph) -> dict[str, int]:
    return {gate.stem: len(list(graph.query(gate.read_text(encoding="utf-8")))) for gate in GATES}


def reasons(graph: Graph, stem: str) -> list[str]:
    query = (PACK / "gates" / f"{stem}.rq").read_text(encoding="utf-8")
    return sorted(str(row.reason) for row in graph.query(query))


def verdict(graph: Graph) -> tuple[dict[str, int], bool]:
    fired = {stem: rows for stem, rows in gate_rows(graph).items() if rows}
    conforms, _, _ = validate(graph, shacl_graph=str(PACK / "ontology" / "shapes.ttl"),
                              inference="none", advanced=True)
    return fired, conforms


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
    assert sorted(str(e).rsplit("#", 1)[1] for e in operationalized) == OPERATIONALIZED
    composed = {str(s).rsplit("#", 1)[1] for s in graph.subjects(SD.composedOf, None)}
    assert sorted(composed) == OPERATIONALIZED
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


# --- Adversarial mutants from the round-0 court (each was ADMITTED before the fix) ---


def test_retyping_a_composed_strategy_as_stub_does_not_escape_the_falsifier_gate() -> None:
    graph = load(*GRAPH_FILES)
    graph.remove((SD["strategy-11"], SD.hasFalsifier, None))
    graph.add((SD["strategy-11"], RDF.type, SD.StrategyStub))
    fired, conforms = verdict(graph)
    assert fired == {"010_strategy_requires_falsifier": 1}
    assert reasons(graph, "010_strategy_requires_falsifier") == ["strategy-without-falsifier"]
    assert conforms is False


def test_stub_retype_with_falsifier_kept_is_still_refused_by_shacl() -> None:
    graph = load(*GRAPH_FILES)
    graph.add((SD["strategy-11"], RDF.type, SD.StrategyStub))
    fired, conforms = verdict(graph)
    assert fired == {}
    assert conforms is False


def test_untyped_node_with_composition_needs_a_falsifier() -> None:
    graph = load(*GRAPH_FILES)
    graph.add((URIRef("urn:example:loose"), SD.composedOf, SD["strategy-11-step-1"]))
    assert reasons(graph, "010_strategy_requires_falsifier") == ["strategy-without-falsifier"]


@pytest.mark.parametrize("statement", ["", "   ", "\t\n", "too short", "x y z w v u t"])
def test_blank_or_trivial_refutation_statement_is_refused(statement: str) -> None:
    graph = load(*GRAPH_FILES)
    falsifier = graph.value(SD["strategy-11"], SD.hasFalsifier)
    graph.set((falsifier, SD.refutedWhen, Literal(statement)))
    fired, conforms = verdict(graph)
    assert fired == {"010_strategy_requires_falsifier": 1}
    assert reasons(graph, "010_strategy_requires_falsifier") == ["falsifier-without-refutation-statement"]
    assert conforms is False


def test_refutation_statement_at_the_ten_character_floor_is_admitted() -> None:
    graph = load(*GRAPH_FILES)
    falsifier = graph.value(SD["strategy-11"], SD.hasFalsifier)
    graph.set((falsifier, SD.refutedWhen, Literal(" share<5% 90d ")))
    assert verdict(graph) == ({}, True)


def test_made_up_class_under_a_public_namespace_is_refused() -> None:
    graph = load(*GRAPH_FILES)
    forged = URIRef("http://www.w3.org/ns/org#PrivateRivalLedger")
    graph.set((SD["cond-many-rivals"], SD.aboutClass, forged))
    fired, _ = verdict(graph)
    assert fired == {"020_applicability_public_class_only": 1}
    assert reasons(graph, "020_applicability_public_class_only") == [
        "condition-over-undeclared-class-in-public-namespace"]
    # Data declaring its own class does not admit it: membership is embedded
    # in the generated gate, never read from the data under judgement.
    graph.add((forged, RDF.type, RDFS.Class))
    graph.add((forged, RDFS.subClassOf, URIRef("http://www.w3.org/ns/org#Organization")))
    assert gate_rows(graph)["020_applicability_public_class_only"] == 1


@pytest.mark.parametrize("declared", [
    "http://www.w3.org/ns/org#Organization",
    "http://www.w3.org/ns/prov#Agent",
    "https://schema.org/Product",
    "http://www.w3.org/ns/sosa/Observation",
    "http://www.w3.org/2006/time#Interval",
    "https://ggen.dev/ontology/strategic-doctrine#Actor",
])
def test_declared_public_and_pack_classes_are_admitted(declared: str) -> None:
    graph = load(*GRAPH_FILES)
    graph.set((SD["cond-many-rivals"], SD.aboutClass, URIRef(declared)))
    assert gate_rows(graph)["020_applicability_public_class_only"] == 0


def test_long_literal_on_a_step_node_is_refused() -> None:
    graph = load(*GRAPH_FILES)
    graph.add((SD["strategy-11-step-1"], SD.note, Literal("x" * 500)))
    fired, _ = verdict(graph)
    assert fired == {"050_no_excerpt": 2}
    assert reasons(graph, "050_no_excerpt") == [
        "literal-over-60-chars-on-catalog-node", "literals-over-120-chars-total-on-catalog-node"]


def test_excerpt_split_into_short_literals_is_refused() -> None:
    graph = load(*GRAPH_FILES)
    for index in range(3):
        graph.add((SD["strategy-11"], SD.note, Literal(f"{index}" + "y" * 59)))
    fired, _ = verdict(graph)
    assert fired == {"050_no_excerpt": 1}
    assert reasons(graph, "050_no_excerpt") == ["literals-over-120-chars-total-on-catalog-node"]


def test_public_class_gate_projection_is_current_and_deterministic() -> None:
    projector = PACK / "scripts" / "project_public_classes.py"
    check = subprocess.run([sys.executable, str(projector), "--check"], capture_output=True, text=True, check=False)
    assert check.returncode == 0, check.stderr
    first = subprocess.run([sys.executable, str(projector), "--stdout"], capture_output=True, check=True).stdout
    second = subprocess.run([sys.executable, str(projector), "--stdout"], capture_output=True, check=True).stdout
    gate = PACK / "gates" / "020_applicability_public_class_only.rq"
    assert first == second == gate.read_bytes()
    text = first.decode("utf-8")
    assert "GENERATED by scripts/project_public_classes.py" in text
    assert "<http://www.w3.org/ns/org#Organization>" in text
    assert "<http://www.w3.org/ns/org#PrivateRivalLedger>" not in text
    assert "GRAPH " not in text and "GRAPH<" not in text  # ggen-engine refuses GRAPH clauses (FM-GRAPH-008)


def test_public_class_gate_projection_detects_a_stale_gate(tmp_path: Path) -> None:
    # Real projector against a real copy of the pack with one class removed
    # from the gate: --check must refuse.
    import shutil
    copy = tmp_path / "strategic-doctrine-pack"
    shutil.copytree(PACK, copy)
    gate = copy / "gates" / "020_applicability_public_class_only.rq"
    gate.write_text(gate.read_text(encoding="utf-8").replace(
        "      <http://www.w3.org/ns/org#Organization>,\n", ""), encoding="utf-8")
    check = subprocess.run([sys.executable, str(copy / "scripts" / "project_public_classes.py"), "--check"],
                           capture_output=True, text=True, check=False)
    assert check.returncode == 1
    assert "REFUSED:GATE_PROJECTION_STALE" in check.stderr


# --- Adversarial mutants from the round-1 court (each was ADMITTED before the fix) ---


@pytest.mark.parametrize("flag", ["assertsNotLicensed", "assertsNoEndorsement", "assertsNoTextReproduced"])
def test_contradictory_nonclaim_is_refused_by_gate_and_shacl(flag: str) -> None:
    graph = load(*GRAPH_FILES)
    graph.add((SD["nonclaim-licensing"], SD[flag], Literal(False)))
    fired, conforms = verdict(graph)
    assert fired == {"060_licensing_nonclaim_present": 2}
    assert reasons(graph, "060_licensing_nonclaim_present") == [
        "licensing-nonclaim-absent", "licensing-nonclaim-contradictory"]
    assert conforms is False


def test_contradictory_nonclaim_is_refused_even_beside_a_clean_one() -> None:
    graph = load(*GRAPH_FILES)
    forged = URIRef("urn:example:forged-nonclaim")
    graph.add((forged, RDF.type, CS.NonClaim))
    graph.add((forged, RDFS.comment, Literal("forged")))
    for flag in ("assertsNotLicensed", "assertsNoEndorsement", "assertsNoTextReproduced"):
        graph.add((forged, SD[flag], Literal(True)))
    graph.add((forged, SD.assertsNoEndorsement, Literal("maybe")))
    fired, conforms = verdict(graph)
    assert fired == {"060_licensing_nonclaim_present": 1}
    assert reasons(graph, "060_licensing_nonclaim_present") == ["licensing-nonclaim-contradictory"]
    assert conforms is False


@pytest.mark.parametrize("length", [201, 400, 5000])
def test_long_refutation_statement_is_refused(length: int) -> None:
    graph = load(*GRAPH_FILES)
    falsifier = graph.value(SD["strategy-11"], SD.hasFalsifier)
    graph.set((falsifier, SD.refutedWhen, Literal("z" * length)))
    fired, conforms = verdict(graph)
    # One row for the literal cap; a second for the node total once the
    # falsifier's literals sum past 300 characters.
    assert fired == {"050_no_excerpt": 1 if length <= 280 else 2}
    assert "literal-over-200-chars-on-falsifier-or-effect-node" in reasons(graph, "050_no_excerpt")
    assert conforms is False


def test_refutation_statement_at_the_200_character_cap_is_admitted() -> None:
    graph = load(*GRAPH_FILES)
    falsifier = graph.value(SD["strategy-11"], SD.hasFalsifier)
    graph.set((falsifier, SD.refutedWhen, Literal("r" * 200)))
    assert verdict(graph) == ({}, True)


def test_long_effect_label_is_refused() -> None:
    graph = load(*GRAPH_FILES)
    effect = URIRef("urn:example:effect")
    graph.add((SD["strategy-11"], SD.producesEffect, effect))
    graph.add((effect, RDF.type, SD.StrategicEffect))
    graph.add((effect, RDFS.label, Literal("e" * 400)))
    fired, conforms = verdict(graph)
    assert fired == {"050_no_excerpt": 2}
    assert reasons(graph, "050_no_excerpt") == [
        "literal-over-200-chars-on-falsifier-or-effect-node",
        "literals-over-300-chars-total-on-falsifier-or-effect-node"]
    assert conforms is False


def test_untyped_effect_split_into_short_literals_is_refused() -> None:
    # Untyped object of sd:producesEffect: the gate still bounds it, and the
    # per-node total catches an excerpt split into several short literals.
    graph = load(*GRAPH_FILES)
    effect = URIRef("urn:example:untyped-effect")
    graph.add((SD["strategy-11"], SD.producesEffect, effect))
    for index in range(4):
        graph.add((effect, SD.note, Literal(f"{index}" + "q" * 99)))
    assert reasons(graph, "050_no_excerpt") == ["literals-over-300-chars-total-on-falsifier-or-effect-node"]


@pytest.mark.parametrize("mutation", ["contradictory-nonclaim", "long-falsifier", "long-effect"])
def test_runner_refuses_round_one_mutants_as_pass_witnesses(mutation: str, tmp_path: Path) -> None:
    # Real runner subprocess over a real mutant built from the real pass witness.
    base = (PACK / "witnesses" / "pass" / "040_step_order_total.ttl").read_text(encoding="utf-8")
    if mutation == "contradictory-nonclaim":
        assert "sd:assertsNotLicensed true ;" in base
        text = base.replace("sd:assertsNotLicensed true ;", "sd:assertsNotLicensed true , false ;")
    elif mutation == "long-falsifier":
        text = base + '\nw:falsifier sd:note "' + "f" * 400 + '" .\n'
    else:
        text = base + ('\nw:strategy sd:producesEffect w:eff .\nw:eff a sd:StrategicEffect ; rdfs:label "'
                       + "g" * 400 + '" .\n')
    witness = tmp_path / "mutant.ttl"
    witness.write_text(text, encoding="utf-8")
    run = subprocess.run([sys.executable, str(PACK / "runners" / "semantic_runner.py"),
                          "--gate", str(PACK / "gates" / "040_step_order_total.rq"),
                          "--witness", str(witness), "--expectation", "pass"],
                         capture_output=True, text=True, check=False)
    assert run.returncode == 2, run.stdout + run.stderr
    assert "REFUSED_" in run.stderr
    # Gate twin fires independently of SHACL.
    graph = Graph()
    graph.parse(witness, format="turtle")
    stem = "060_licensing_nonclaim_present" if mutation == "contradictory-nonclaim" else "050_no_excerpt"
    assert gate_rows(graph)[stem] >= 1
