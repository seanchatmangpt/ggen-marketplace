from pathlib import Path
from rdflib import Graph
from rdflib.plugins.sparql.parser import parseQuery

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "ontology.r77-repository-universe.ttl"
FIXTURE = ROOT / "fixtures/r77-repository-universe.ttl"
QUERIES = ROOT / "queries/r77"


def test_r77_graph_and_all_sensors_parse_and_execute():
    graph = Graph()
    graph.parse(ROOT / "ontology.r76-structural-census.ttl", format="turtle")
    graph.parse(ONTOLOGY, format="turtle")
    graph.parse(FIXTURE, format="turtle")
    sensors = sorted(QUERIES.glob("*.rq"))
    assert len(sensors) == 50
    for sensor in sensors:
        text = sensor.read_text()
        parseQuery(text)
        list(graph.query(text))


def test_r77_is_ggen_owned_and_read_only():
    ggen = (ROOT / "ggen.toml").read_text()
    collector = (ROOT / "scripts/r77_repository_universe.py").read_text()
    assert "r77-exact-repository-universe-frontier" in ggen
    assert "50-clean-repository-universe-frontier.rq" in ggen
    assert "/user/repos" in collector and "/users/" in collector
    assert "urllib.request.Request" in collector
    assert "POST" not in collector and "PATCH" not in collector and "DELETE" not in collector


def test_r77_preserves_dual_revops_and_exact_identity():
    fixture = FIXTURE.read_text()
    assert "RevenueFromCustomer" not in fixture or "RevenueForCustomer" in fixture
    assert "exactHead" in fixture
    assert "RepositoryUniverse" in fixture
    assert "qualificationReceipt" not in fixture or "ALIVE" in fixture
