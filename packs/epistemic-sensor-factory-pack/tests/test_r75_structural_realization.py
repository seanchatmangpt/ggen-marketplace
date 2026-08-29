from pathlib import Path

from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "ontology.r75-structural-realization.ttl"
FIXTURE = ROOT / "fixtures" / "r75-structural-realization.ttl"
QUERIES = sorted((ROOT / "queries").glob("50*_r75_*.rq"))
EXPECTED_QUERY_COUNT = 50


def main():
    graph = Graph()
    graph.parse(ONTOLOGY, format="turtle")
    graph.parse(FIXTURE, format="turtle")
    assert len(QUERIES) == EXPECTED_QUERY_COUNT, len(QUERIES)
    for query in QUERIES:
        text = query.read_text()
        assert "https://ggen.dev/implement/r75#" in text
        list(graph.query(text))
    print(f"R75 structural realization court: {len(QUERIES)}/{EXPECTED_QUERY_COUNT} courts PASS")


if __name__ == "__main__":
    main()
