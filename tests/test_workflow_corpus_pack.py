"""Courts for packs/workflow-corpus-pack (lane 8, v26.9.30 wave).

Structural courts (manifest, pin conformance, gate shape, fixture structure)
plus the REAL semantic court (qualification/verify.py subprocess) and two
MUTATION falsifiers: the shared gates must fire on a real corpus fixture with
one pinned property surgically removed -- a gate that only fires on synthetic
witnesses would be vacuous against the corpus it exists to police (C05
mutation lens).

Lane-safety: this module asserts ONLY lane-8-owned paths (ontology.ttl,
pack.toml, gates f000_/f01_..f04_, witnesses/, qualification/, fixtures/
01-04). Lanes 9/10 author fixtures 05-12 and gates f05_*..f12_* concurrently;
nothing here globs or asserts on their subtrees.
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import rdflib

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "workflow-corpus-pack"
WFC = rdflib.Namespace("https://ggen.dev/ontology/workflow-corpus#")
PROV = rdflib.Namespace("http://www.w3.org/ns/prov#")
XSD = rdflib.Namespace("http://www.w3.org/2001/XMLSchema#")

OWNED_FIXTURES = {
    "01": PACK / "fixtures" / "01-filesystem-network-failure-isolation",
    "02": PACK / "fixtures" / "02-qualification-gated-release",
    "03": PACK / "fixtures" / "03-approval-halt-resume",
    "04": PACK / "fixtures" / "04-provider-refusal-alternate",
}
OWNED_GATES = sorted(
    path
    for path in (PACK / "gates").glob("*.rq")
    if path.name.startswith(("f000_", "f01_", "f02_", "f03_", "f04_"))
)

# Pinned capability IDs, verbatim from docs/jira/v26.9.30/RESOLUTIONS.md.
PINNED_CAPABILITY_IDS = {
    # fscap
    "File.Read", "File.Write", "File.Copy", "File.Move", "File.Delete",
    "File.Exists", "Dir.List", "Dir.Mkdir", "Dir.Remove",
    # ncap
    "Http.Request", "Http.Get", "Http.Post", "Remote.Invoke", "Endpoint.Resolve",
    # dcp
    "Domain.Action.Invoke", "Domain.Query.Read", "Domain.Change.Apply",
    # pcap
    "Process.Spawn", "Process.Supervise", "Process.Signal", "Process.Link",
    # escap
    "Event.Emit", "Event.Subscribe", "State.Observe", "State.Query",
    # scap
    "Schedule.At", "Schedule.Cron", "Schedule.Delay",
    # dcap
    "Durability.Checkpoint", "Durability.Replay", "Durability.Resume",
    "Workflow.Halt", "Workflow.Resume",
    # ocap
    "Observation.Tap", "Observation.Sample", "Telemetry.Emit",
    # aacap
    "A2A.Invoke", "A2A.Discover", "A2A.Await",
    # authcap
    "Authority.Verify", "Authority.Grant", "Actuation.Execute",
    # ecap
    "Evidence.Establish", "Evidence.Bind", "Receipt.Sign", "Provenance.Record",
}

PINNED_CLASSES = {
    "WorkflowFixture", "ExpectedDecomposition", "ExpectedOutcome",
    "ProviderClosure", "Falsifier",
}
PINNED_PROPERTIES = {
    "fixtureNumber", "goal", "task", "capability", "expectedDecomposition",
    "expectedOutcome", "requiredEvidence", "requiredAuthority",
    "expectedProviderClosure", "forbiddenRealization", "falsifierStatement",
}
PINNED_STRING_RANGES = {
    "goal", "capability", "requiredEvidence", "requiredAuthority",
    "forbiddenRealization", "falsifierStatement",
}


def pack_graph() -> rdflib.Graph:
    graph = rdflib.Graph()
    graph.parse(PACK / "ontology.ttl", format="turtle")
    return graph


def fixture_graph(directory: Path) -> rdflib.Graph:
    graph = pack_graph()
    graph.parse(directory / "fixture.ttl", format="turtle")
    return graph


# --- manifest contract (real ggen denies unknown [pack] keys) --------------

def test_pack_table_admits_only_pinned_keys() -> None:
    document = tomllib.loads((PACK / "pack.toml").read_text(encoding="utf-8"))
    assert set(document["pack"]) == {"name", "version", "description"}
    assert document["pack"]["name"] == "workflow-corpus-pack"


def test_no_forbidden_pack_files() -> None:
    # FM-PACK-012 (no shapes.ttl) and FM-CONFIG-102 (no non-schema ggen.toml).
    assert not (PACK / "shapes.ttl").exists()
    assert not (PACK / "ggen.toml").exists()


# --- wfc: pin conformance (ontology.ttl defines EXACTLY the pinned terms) ---

def test_ontology_defines_exactly_the_pinned_classes() -> None:
    graph = pack_graph()
    defined = {
        str(term.split("#")[-1])
        for term in graph.subjects(rdflib.RDF.type, rdflib.RDFS.Class)
        if str(term).startswith(str(WFC))
    }
    assert defined == PINNED_CLASSES
    for name in PINNED_CLASSES:
        term = WFC[name]
        assert (term, rdflib.RDF.type, PROV.Entity) in graph, name


def test_ontology_defines_exactly_the_pinned_properties() -> None:
    graph = pack_graph()
    defined = {
        str(term.split("#")[-1])
        for term in graph.subjects(rdflib.RDF.type, rdflib.RDF.Property)
        if str(term).startswith(str(WFC))
    }
    assert defined == PINNED_PROPERTIES


def test_ontology_property_ranges_match_the_pin() -> None:
    graph = pack_graph()
    for name in PINNED_STRING_RANGES:
        assert (WFC[name], rdflib.RDFS.range, XSD.string) in graph, name
    assert (WFC["fixtureNumber"], rdflib.RDFS.range, XSD.integer) in graph


# --- gate shape (violation-row SELECTs; E0013 ORDER BY) ---------------------

def test_owned_gates_exist_and_carry_order_by() -> None:
    assert len(OWNED_GATES) == 10
    for gate in OWNED_GATES:
        text = gate.read_text(encoding="utf-8")
        assert "SELECT" in text, gate.name
        assert "ORDER BY" in text, gate.name
        assert text.lstrip().startswith("# MESSAGE:"), gate.name


# --- fixture structure (fixtures 01-04 are lane-8-owned) --------------------

@pytest.mark.parametrize("number", sorted(OWNED_FIXTURES))
def test_fixture_directory_contract(number: str) -> None:
    directory = OWNED_FIXTURES[number]
    assert (directory / "fixture.ttl").is_file()
    assert (directory / "expected.md").is_file()
    assert directory.name.startswith(f"{number}-")


@pytest.mark.parametrize("number", sorted(OWNED_FIXTURES))
def test_fixture_is_one_individual_with_matching_number(number: str) -> None:
    graph = fixture_graph(OWNED_FIXTURES[number])
    fixtures = list(graph.subjects(rdflib.RDF.type, WFC.WorkflowFixture))
    assert len(fixtures) == 1
    numbers = list(graph.objects(fixtures[0], WFC.fixtureNumber))
    assert [int(value) for value in numbers] == [int(number)]
    assert list(graph.objects(fixtures[0], WFC.goal))
    assert list(graph.objects(fixtures[0], WFC.falsifierStatement))
    assert list(graph.objects(fixtures[0], WFC.expectedOutcome))


@pytest.mark.parametrize("number", sorted(OWNED_FIXTURES))
def test_fixture_capabilities_are_pinned_ids(number: str) -> None:
    graph = fixture_graph(OWNED_FIXTURES[number])
    for capability in graph.objects(None, WFC.capability):
        assert str(capability) in PINNED_CAPABILITY_IDS, (number, capability)


def test_fixture_tasks_are_prov_activities() -> None:
    for number in sorted(OWNED_FIXTURES):
        graph = fixture_graph(OWNED_FIXTURES[number])
        for task in graph.objects(None, WFC.task):
            assert (task, rdflib.RDF.type, PROV.Activity) in graph, (number, task)


# --- real semantic court ----------------------------------------------------

def test_semantic_court_admits() -> None:
    pytest.importorskip("rdflib")
    result = subprocess.run(
        [sys.executable, "qualification/verify.py"],
        cwd=PACK,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.startswith("ADMITTED:workflow-corpus semantic court")


# --- mutation falsifiers (the corpus itself must be able to fire the gates) --

def _rowcount(gate: Path, graph: rdflib.Graph) -> int:
    return len(list(graph.query(gate.read_text(encoding="utf-8"))))


def test_mutation_removing_falsifier_from_real_fixture_fires_gate() -> None:
    gate = PACK / "gates" / "f000_fixture_missing_falsifier.rq"
    graph = fixture_graph(OWNED_FIXTURES["01"])
    assert _rowcount(gate, graph) == 0
    graph.remove((None, WFC.falsifierStatement, None))
    assert _rowcount(gate, graph) >= 1


def test_mutation_removing_authority_from_real_fixture_fires_gate() -> None:
    gate = PACK / "gates" / "f000_consequential_task_without_required_authority.rq"
    graph = fixture_graph(OWNED_FIXTURES["02"])
    assert _rowcount(gate, graph) == 0
    graph.remove((None, WFC.requiredAuthority, None))
    assert _rowcount(gate, graph) >= 1


def test_mutation_sharing_outcome_across_fixture01_tasks_fires_gate() -> None:
    gate = PACK / "gates" / "f01_file_network_failure_isolation.rq"
    graph = fixture_graph(OWNED_FIXTURES["01"])
    assert _rowcount(gate, graph) == 0
    # Surgery: make the post task also expect the write task's success outcome
    # (the shared-outcome-node corruption channel).
    write = graph.value(None, WFC.capability, rdflib.Literal("File.Write"))
    post = graph.value(None, WFC.capability, rdflib.Literal("Http.Post"))
    assert write is not None and post is not None
    outcome = graph.value(write, WFC.expectedOutcome)
    assert outcome is not None
    graph.add((post, WFC.expectedOutcome, outcome))
    assert _rowcount(gate, graph) >= 1
