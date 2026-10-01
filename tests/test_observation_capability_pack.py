"""Anti-vacuity court for packs/observation-capability-pack.

Real collaborators only: the real on-disk Turtle parsed by rdflib and the real
SPARQL gate files executed by rdflib against (a) the pack ontology alone, (b)
the positive fixture, and (c) each negative fixture. Nothing is mocked.

The law this court guards: a gate with no witnessed refusal carries no bits.
Every gate in gates/ must return zero rows on conforming data (ontology +
positive fixture) and >= 1 row on its named negative fixture. The evidence-first
law is doubly witnessed: shape A (no evidence requirement) by
negative-observation-without-evidence.ttl and shape B (evidenceCapable false) by
negative-evidence-incapable-tap.ttl. The ProviderAvailable != Authorized witness
(negative-authority-unbound-consequential-sink.ttl) carries providerAvailable
true on the offending realization and must STILL be refused.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from rdflib import Graph

REPO_ROOT = Path(__file__).resolve().parents[1]
PACK = REPO_ROOT / "packs" / "observation-capability-pack"
ONTOLOGY = PACK / "ontology.ttl"
GATES_DIR = PACK / "gates"
FIXTURES = PACK / "qualification" / "fixtures"

PINNED_IDS = ("Observation.Tap", "Observation.Sample", "Telemetry.Emit")

GATE_TO_NEGATIVE = {
    "010_capability_requires_realization.rq": "negative-capability-without-realization.ttl",
    "020_realization_requires_qualification.rq": "negative-realization-without-qualification.ttl",
    "030_delivery_semantics_required.rq": "negative-delivery-semantics-missing.ttl",
    "040_observation_requires_evidence.rq": "negative-observation-without-evidence.ttl",
    "050_consequential_requires_authority.rq": "negative-authority-unbound-consequential-sink.ttl",
}

GATE_040_SHAPE_B = "negative-evidence-incapable-tap.ttl"


def _parse(*sources: Path) -> Graph:
    graph = Graph()
    for source in sources:
        graph.parse(source, format="turtle")
    return graph


def _gate_rows(graph: Graph, gate: Path) -> list[tuple[str, ...]]:
    return [tuple(str(term) for term in row) for row in graph.query(gate.read_text())]


def _all_gates() -> list[Path]:
    return sorted(GATES_DIR.glob("*.rq"))


def test_layout_is_complete() -> None:
    assert ONTOLOGY.is_file()
    assert (PACK / "pack.toml").is_file()
    assert (PACK / "README.md").is_file()
    assert len(_all_gates()) == 5
    assert (FIXTURES / "positive-conforming-instance.ttl").is_file()
    for negative in (*GATE_TO_NEGATIVE.values(), GATE_040_SHAPE_B):
        assert (FIXTURES / negative).is_file()


@pytest.mark.parametrize("ttl", [ONTOLOGY, *(FIXTURES / n for n in (*GATE_TO_NEGATIVE.values(), GATE_040_SHAPE_B)),
                                 FIXTURES / "positive-conforming-instance.ttl"])
def test_turtle_parses(ttl: Path) -> None:
    graph = Graph()
    graph.parse(ttl, format="turtle")
    assert len(graph) > 0


def _quoted(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def test_pinned_capability_ids_present() -> None:
    graph = _parse(ONTOLOGY)
    for dotted in PINNED_IDS:
        query = (
            "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> "
            "PREFIX dcterms: <http://purl.org/dc/terms/> "
            "SELECT ?c WHERE { ?c rdfs:label ?l ; dcterms:identifier ?i . "
            f"FILTER(?l = {_quoted(dotted)} && ?i = {_quoted(dotted)}) }}"
        )
        assert list(graph.query(query)), f"pinned id {dotted} missing label/identifier"


def test_ontology_is_conforming_all_gates_silent() -> None:
    graph = _parse(ONTOLOGY)
    for gate in _all_gates():
        rows = _gate_rows(graph, gate)
        assert rows == [], f"{gate.name} fired on the pack's own ontology: {rows[:3]}"


def test_positive_fixture_is_conforming_alone_and_unioned() -> None:
    positive = FIXTURES / "positive-conforming-instance.ttl"
    for graph in (_parse(positive), _parse(ONTOLOGY, positive)):
        for gate in _all_gates():
            rows = _gate_rows(graph, gate)
            assert rows == [], f"{gate.name} fired on POSITIVE data: {rows[:3]}"


def test_every_gate_has_a_negative_fixture() -> None:
    gates = {gate.name: gate for gate in _all_gates()}
    assert set(GATE_TO_NEGATIVE) == set(gates), "gate/fixture map must cover every gate"
    for negative in (*GATE_TO_NEGATIVE.values(), GATE_040_SHAPE_B):
        assert (FIXTURES / negative).is_file()


@pytest.mark.parametrize(("gate_name", "negative"), sorted(GATE_TO_NEGATIVE.items()))
def test_negative_fixture_fires_its_gate(gate_name: str, negative: str) -> None:
    graph = _parse(ONTOLOGY, FIXTURES / negative)
    rows = _gate_rows(graph, GATES_DIR / gate_name)
    assert rows, f"{negative} does NOT fire {gate_name}: the gate carries no witnessed refusal"


def test_gate_040_shape_b_evidence_incapable_tap_is_refused() -> None:
    """A tap that declares itself unable to produce evidence is refused even
    when it states SOME evidence requirement."""
    graph = _parse(ONTOLOGY, FIXTURES / GATE_040_SHAPE_B)
    rows = _gate_rows(graph, GATES_DIR / "040_observation_requires_evidence.rq")
    assert rows, "evidence-incapable realization must be refused (shape B)"
    assert any(row[1] == "evidence-incapable-realization" for row in rows), rows


def test_provider_available_never_discharges_authority() -> None:
    """The 050 witness sets providerAvailable true and must STILL be refused."""
    witness = FIXTURES / "negative-authority-unbound-consequential-sink.ttl"
    graph = _parse(ONTOLOGY, witness)
    available = list(
        graph.query(
            "PREFIX ocap: <https://ggen.dev/ontology/observation-capability#> "
            "SELECT ?r WHERE { ?r ocap:providerAvailable true }"
        )
    )
    assert available, "witness must actually carry providerAvailable true"
    rows = _gate_rows(graph, GATES_DIR / "050_consequential_requires_authority.rq")
    assert rows, "a provider-available realization onto a consequential sink must still be refused"


def test_gate_050_silent_for_nonconsequential_sink_counterfactual() -> None:
    """Same capability (Telemetry.Emit), different sink: the telemetry-execute
    realization emits onto a non-consequential stream WITHOUT authority and
    MUST be admitted."""
    graph = _parse(ONTOLOGY)
    rows = _gate_rows(graph, GATES_DIR / "050_consequential_requires_authority.rq")
    for row in rows:
        assert "telemetry-execute" not in row[0], f"non-consequential sink emit wrongly refused: {row}"


def test_evidence_records_are_earl_anchored() -> None:
    """Every evidence record kind must be re-expressible as an EARL assertion
    (rdfs:seeAlso earl:Assertion) -- the EARL composition is load-bearing."""
    graph = _parse(ONTOLOGY)
    rows = list(
        graph.query(
            "PREFIX ocap: <https://ggen.dev/ontology/observation-capability#> "
            "PREFIX earl: <http://www.w3.org/ns/earl#> "
            "SELECT ?kind WHERE { ?kind a ocap:EvidenceRecord . "
            "FILTER NOT EXISTS { ?kind rdfs:seeAlso earl:Assertion } }"
        )
    )
    assert rows == [], f"evidence record kinds without an EARL anchor: {rows}"
