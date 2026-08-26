from pathlib import Path

from rdflib import Graph
from rdflib.plugins.sparql.parser import parseQuery

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "ontology.r76-structural-census.ttl"
FIXTURE = ROOT / "fixtures/r76-structural-census.ttl"
QUERIES = ROOT / "queries/r76-structural-census"


def test_r76_graph_and_all_sensors_parse_and_execute():
    graph = Graph()
    graph.parse(ONTOLOGY, format="turtle")
    graph.parse(FIXTURE, format="turtle")
    sensors = sorted(QUERIES.glob("*.rq"))
    assert len(sensors) == 50
    for sensor in sensors:
        text = sensor.read_text()
        parseQuery(text)
        list(graph.query(text))


def test_r76_preserves_dual_revops_and_structural_chain():
    ontology = ONTOLOGY.read_text()
    fixture = FIXTURE.read_text()
    assert "RevenueFromCustomer" in ontology
    assert "RevenueForCustomer" in ontology
    assert "existingStructure" in fixture
    assert "desiredStructure" in fixture
    assert "ontologySource" in fixture
    assert "qualificationReceipt" in fixture


def test_r76_is_ggen_owned_and_non_actuating():
    ggen = (ROOT / "ggen.toml").read_text()
    assert "r76-portfolio-structural-census" in ggen
    assert "050_clean_structural_frontier.rq" in ggen
    assert "r76-structural-census-frontier.json.tera" in ggen
    for source in (ONTOLOGY.read_text(), FIXTURE.read_text()):
        assert "actuationPerformed true" not in source
        assert "consequential_do = true" not in source
