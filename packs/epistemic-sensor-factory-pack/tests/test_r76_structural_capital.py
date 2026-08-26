from pathlib import Path
from rdflib import Graph, Namespace
from rdflib.plugins.sparql.parser import parseQuery

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "ontology.r76-structural-capital-compiler.ttl"
FIXTURE = ROOT / "fixtures/r76-structural-capital.ttl"
QUERIES = ROOT / "queries/r76-structural-capital"
ESF = Namespace("https://ggen.dev/ontology/epistemic-sensor-factory#")


def graph():
    value = Graph()
    value.parse(ROOT / "ontology.r75-throughput-learning.ttl", format="turtle")
    value.parse(ONTOLOGY, format="turtle")
    value.parse(FIXTURE, format="turtle")
    return value


def test_r76_all_semantic_courts_parse_and_execute():
    value = graph()
    courts = sorted(QUERIES.glob("*.rq"))
    assert len(courts) >= 50
    for court in courts:
        text = court.read_text()
        parseQuery(text)
        list(value.query(text))


def test_r76_reference_factory_reaches_phase_change_court():
    rows = list(graph().query((QUERIES / "050_phase_change_1000x_candidate.rq").read_text()))
    assert len(rows) == 1
    assert "factory-candidate" in str(rows[0][0])


def test_r76_preserves_adversarial_incomplete_candidate():
    rows = list(graph().query((QUERIES / "003_candidate_without_canonical_primitive.rq").read_text()))
    assert any("adapter-candidate" in str(row[0]) for row in rows)


def test_r76_is_ggen_owned_and_non_actuating():
    ggen = (ROOT / "ggen.toml").read_text()
    assert "r76-structural-capital-plan" in ggen
    assert "r76-structural-capital-plan.json.tera" in ggen
    assert "consequential_do" in (ROOT / "templates/r76-structural-capital-plan.json.tera").read_text()
