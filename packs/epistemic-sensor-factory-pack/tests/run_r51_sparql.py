#!/usr/bin/env python3
from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "r51-consumer-admission-frontier.ttl"


def main():
    graph = Graph()
    graph.parse(ROOT / "ontology.ttl", format="turtle")
    graph.parse(FIXTURE, format="turtle")
    queries = sorted(
        p for p in (ROOT / "queries").glob("*.rq")
        if p.name[:3].isdigit() and 401 <= int(p.name[:3]) <= 450
    )
    assert len(queries) == 50, len(queries)
    results = {}
    for path in queries:
        rows = list(graph.query(path.read_text()))
        results[path.name] = rows
        print(f"PASS {path.name} rows={len(rows)}")
    assert int(results["401_consumer_admission_candidate_census.rq"][0][0]) == 4
    assert len(results["402_exact_head_identity_gaps.rq"]) == 0
    assert len(results["426_ambient_do_violations.rq"]) == 0
    assert int(results["430_admitted_standing_census.rq"][0][0]) == 1
    assert len(results["433_clean_admission_frontier.rq"]) == 2
    assert int(results["448_independently_admissible_census.rq"][0][0]) == 2
    assert int(results["449_consumer_admission_10x_shortfall.rq"][0][0]) == 8
    print("R51_SPARQL_EXECUTION=50 ALIVE independently_admissible=2 admission_shortfall=8")


if __name__ == "__main__":
    main()
