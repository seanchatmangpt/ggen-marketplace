#!/usr/bin/env python3
from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
QUERY_DIR = ROOT / "queries" / "r51"
FIXTURE = ROOT / "fixtures" / "r51-transitive-propagation.ttl"
ONTOLOGY = ROOT / "ontology.ttl"
GGEN = ROOT / "ggen.toml"


def main() -> None:
    queries = sorted(QUERY_DIR.glob("*.rq"))
    assert len(queries) == 50, f"expected 50 R51 sensors, got {len(queries)}"

    graph = Graph()
    graph.parse(ONTOLOGY, format="turtle")
    graph.parse(FIXTURE, format="turtle")
    for query in queries:
        list(graph.query(query.read_text()))

    text = ONTOLOGY.read_text()
    assert "odrl:prohibition [ odrl:action odrl:execute ]" in text
    assert "esf:PropagationEdge a prov:Activity" in text
    assert "esf:TransitiveTarget a dcat:Resource" in text
    assert "esf:PropagationReceipt a prov:Entity" in text

    fixture = FIXTURE.read_text()
    for sha in (
        "9fe8fe237601a08817cbc14f05e8dd93186e3711",
        "3604bd0bb0834477fca02453ad787009bffb06dd",
        "a6d4829d9ba2006e473515e4049bb3b785b677f3",
    ):
        assert sha in fixture

    ggen = GGEN.read_text()
    assert 'name = "transitive-propagation-plan"' in ggen
    assert 'query = { file = "queries/550_transitive_propagation_plan.rq" }' in ggen
    assert 'template = { file = "templates/transitive-propagation-plan.json.tera" }' in ggen
    assert 'output_file = "generated/epistemic-sensor-factory/transitive-propagation-plan.json"' in ggen

    print("R51_ALIVE sensors=50 exact_targets=3 consequential_do=false")


if __name__ == "__main__":
    main()
