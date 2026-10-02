"""Anti-vacuity court for packs/capability-ecology-pack.

Real collaborators only: the real on-disk Turtle parsed by rdflib and the real
SPARQL gate files executed by rdflib against (a) the pack ontology alone, (b)
the positive fixture, and (c) each negative fixture. Nothing is mocked.

The law this court guards (fanout-first: courts kill, not pre-thinking): a gate
with no witnessed refusal carries no bits. Every gate in gates/ must return zero
rows on conforming data (ontology + positive fixture) and >= 1 row on its named
negative fixture in qualification/fixtures/. The ProviderAvailable != Authorized
witness (escap_negative-authority-unbound-consequential-topic.ttl) carries
providerAvailable true on the offending realization and must STILL be refused:
provider availability never discharges authority.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from rdflib import Graph

REPO_ROOT = Path(__file__).resolve().parents[1]
PACK = REPO_ROOT / "packs" / "capability-ecology-pack"
ONTOLOGY = PACK / "ontology/event-state.ttl"
GATES_DIR = PACK / "gates"
FIXTURES = PACK / "qualification" / "fixtures"

PINNED_IDS = ("Event.Emit", "Event.Subscribe", "State.Observe", "State.Query")

GATE_TO_NEGATIVE = {
    "escap_010_capability_requires_realization.rq": "escap_negative-capability-without-realization.ttl",
    "escap_020_realization_requires_qualification.rq": "escap_negative-realization-without-qualification.ttl",
    "escap_030_delivery_semantics_required.rq": "escap_negative-delivery-semantics-missing.ttl",
    "escap_040_observation_requires_evidence.rq": "escap_negative-observation-without-evidence.ttl",
    "escap_050_consequential_requires_authority.rq": "escap_negative-authority-unbound-consequential-topic.ttl",
}


def _parse(*sources: Path) -> Graph:
    graph = Graph()
    for source in sources:
        graph.parse(source, format="turtle")
    return graph


def _gate_rows(graph: Graph, gate: Path) -> list[tuple[str, ...]]:
    return [tuple(str(term) for term in row) for row in graph.query(gate.read_text())]


def _all_gates() -> list[Path]:
    return sorted(GATES_DIR.glob("escap_*.rq"))


def test_layout_is_complete() -> None:
    assert ONTOLOGY.is_file()
    assert (PACK / "pack.toml").is_file()
    assert (PACK / "families" / "event-state.md").is_file()
    assert len(_all_gates()) == 5
    assert (FIXTURES / "escap_positive-conforming-instance.ttl").is_file()
    for negative in GATE_TO_NEGATIVE.values():
        assert (FIXTURES / negative).is_file()


@pytest.mark.parametrize("ttl", [ONTOLOGY, *(FIXTURES / n for n in GATE_TO_NEGATIVE.values()),
                                 FIXTURES / "escap_positive-conforming-instance.ttl"])
def test_turtle_parses(ttl: Path) -> None:
    graph = Graph()
    graph.parse(ttl, format="turtle")
    assert len(graph) > 0


def test_pinned_capability_ids_present() -> None:
    graph = _parse(ONTOLOGY)
    for dotted in PINNED_IDS:
        query = (
            "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> "
            "PREFIX dcterms: <http://purl.org/dc/terms/> "
            "SELECT ?c WHERE { ?c rdfs:label ?l ; dcterms:identifier ?i . "
            f"FILTER(?l = {json_literal(dotted)} && ?i = {json_literal(dotted)}) }}"
        )
        assert list(graph.query(query)), f"pinned id {dotted} missing label/identifier"


def json_literal(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def test_ontology_is_conforming_all_gates_silent() -> None:
    graph = _parse(ONTOLOGY)
    for gate in _all_gates():
        rows = _gate_rows(graph, gate)
        assert rows == [], f"{gate.name} fired on the pack's own ontology: {rows[:3]}"


def test_positive_fixture_is_conforming_alone_and_unioned() -> None:
    positive = FIXTURES / "escap_positive-conforming-instance.ttl"
    for graph in (_parse(positive), _parse(ONTOLOGY, positive)):
        for gate in _all_gates():
            rows = _gate_rows(graph, gate)
            assert rows == [], f"{gate.name} fired on POSITIVE data: {rows[:3]}"


def test_every_gate_has_a_negative_fixture() -> None:
    gates = {gate.name: gate for gate in _all_gates()}
    assert set(GATE_TO_NEGATIVE) == set(gates), "gate/fixture map must cover every gate"
    for negative in GATE_TO_NEGATIVE.values():
        assert (FIXTURES / negative).is_file()


@pytest.mark.parametrize(("gate_name", "negative"), sorted(GATE_TO_NEGATIVE.items()))
def test_negative_fixture_fires_its_gate(gate_name: str, negative: str) -> None:
    graph = _parse(ONTOLOGY, FIXTURES / negative)
    rows = _gate_rows(graph, GATES_DIR / gate_name)
    assert rows, f"{negative} does NOT fire {gate_name}: the gate carries no witnessed refusal"


def test_provider_available_never_discharges_authority() -> None:
    """The 050 witness sets providerAvailable true and must STILL be refused."""
    witness = FIXTURES / "escap_negative-authority-unbound-consequential-topic.ttl"
    graph = _parse(ONTOLOGY, witness)
    available = list(
        graph.query(
            "PREFIX escap: <https://ggen.dev/ontology/event-state-capability#> "
            "SELECT ?r WHERE { ?r escap:providerAvailable true }"
        )
    )
    assert available, "witness must actually carry providerAvailable true"
    rows = _gate_rows(graph, GATES_DIR / "escap_050_consequential_requires_authority.rq")
    assert rows, "a provider-available realization onto a consequential topic must still be refused"


def test_gate_050_silent_for_nonconsequential_topic_counterfactual() -> None:
    """Same capability (Event.Emit), different topic: the telemetry realization
    emits onto a non-consequential topic WITHOUT authority and MUST be admitted."""
    graph = _parse(ONTOLOGY)
    rows = _gate_rows(graph, GATES_DIR / "escap_050_consequential_requires_authority.rq")
    for row in rows:
        assert "telemetry" not in row[0], f"non-consequential topic emit wrongly refused: {row}"
