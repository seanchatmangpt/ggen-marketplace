from pathlib import Path
from rdflib import Graph
from rdflib.plugins.sparql.parser import parseQuery

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "ontology.r73-structural-revops.ttl"
FIXTURE = ROOT / "fixtures" / "r73-structural-revops.ttl"
QUERIES = sorted((ROOT / "queries").glob("*_r73_*.rq"))
EXPECTED_QUERY_COUNT = 132


def main():
    graph = Graph()
    graph.parse(ONTOLOGY, format="turtle")
    graph.parse(FIXTURE, format="turtle")
    assert len(QUERIES) == EXPECTED_QUERY_COUNT, len(QUERIES)
    assert all("_r73_" in query.name for query in QUERIES)
    for query in QUERIES:
        text = query.read_text()
        assert "https://ggen.dev/measure/r73#" in text
        parseQuery(text)
        list(graph.query(text))
    ontology = ONTOLOGY.read_text()
    assert "RevenueFromCustomer" in ontology
    assert "RevenueForCustomer" in ontology
    assert "BRCE" not in ontology
    print(f"R73 structural RevOps court: {len(QUERIES)}/{EXPECTED_QUERY_COUNT} sensors PASS")


if __name__ == "__main__":
    main()
