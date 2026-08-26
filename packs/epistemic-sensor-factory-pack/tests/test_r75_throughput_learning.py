from pathlib import Path
from rdflib import Graph
from rdflib.plugins.sparql.parser import parseQuery

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "ontology.r75-throughput-learning.ttl"
FIXTURE = ROOT / "fixtures/r75-throughput-learning.ttl"
QUERIES = ROOT / "queries/r75-throughput-learning"


def test_r75_graph_and_all_sensors_parse_and_execute():
    graph = Graph()
    graph.parse(ONTOLOGY, format="turtle")
    graph.parse(FIXTURE, format="turtle")
    sensors = sorted(QUERIES.glob("*.rq"))
    assert len(sensors) >= 39
    for sensor in sensors:
        text = sensor.read_text()
        parseQuery(text)
        list(graph.query(text))


def test_r75_dual_revenue_semantics_remain_distinct():
    text = ONTOLOGY.read_text()
    assert "RevenueFromCustomer" in text
    assert "RevenueForCustomer" in text
    assert "RevenueFromCustomer a rdfs:Class" in text
    assert "RevenueForCustomer a rdfs:Class" in text


def test_r75_is_non_actuating_and_ggen_owned():
    ggen = (ROOT / "ggen.toml").read_text()
    assert "r75-throughput-learning-plan" in ggen
    assert "r75-throughput-learning-plan.json.tera" in ggen
    assert "CONSEQUENTIAL_DO" not in ONTOLOGY.read_text()
