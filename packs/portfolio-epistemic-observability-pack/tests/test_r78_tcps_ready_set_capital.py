from pathlib import Path

from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
QUERIES = ROOT / "queries" / "r78-tcps-ready-set"


def graph() -> Graph:
    g = Graph()
    g.parse(ROOT / "ontology.r78-tcps-ready-set-capital.ttl", format="turtle")
    g.parse(ROOT / "fixtures" / "r78-tcps-ready-set-capital.ttl", format="turtle")
    return g


def test_r78_executes_exact_semantic_family():
    g = graph()
    queries = sorted(QUERIES.glob("*.rq"))
    assert len(queries) == 50, [p.name for p in queries]
    for query in queries:
        list(g.query(query.read_text()))


def test_legality_precedes_priority_and_ready_set_bounds_selection():
    g = graph()
    ns = "https://ggen.dev/ontology/portfolio-epistemic-observability#"
    ex = "https://ggen.dev/fixtures/r78#"
    selected = list(g.query(f"PREFIX peo: <{ns}> SELECT ?c WHERE {{ ?c peo:selected true . }}"))
    assert [str(row.c) for row in selected] == [ex + "candidate-r78"]
    illegal = list(g.query((QUERIES / "004_illegal_high_score_falsifier.rq").read_text()))
    assert len(illegal) == 1
    outside_ready = list(g.query((QUERIES / "007_selected_outside_ready_falsifier.rq").read_text()))
    assert outside_ready == []


def test_clean_crown_is_brokered_receipted_and_non_actuating():
    g = graph()
    rows = list(g.query((QUERIES / "050_clean_allocation_crown.rq").read_text()))
    assert len(rows) == 1
    assert str(rows[0].candidate).endswith("candidate-r78")
    assert int(rows[0].score) == 94
    assert list(g.query((QUERIES / "033_ambient_do_falsifier.rq").read_text())) == []
