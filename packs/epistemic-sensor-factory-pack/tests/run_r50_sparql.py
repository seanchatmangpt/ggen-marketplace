#!/usr/bin/env python3
from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "r50-consumer-evidence-return.ttl"


def main():
    graph = Graph()
    graph.parse(ROOT / "ontology.ttl", format="turtle")
    graph.parse(FIXTURE, format="turtle")
    queries = sorted(
        p for p in (ROOT / "queries").glob("*.rq")
        if p.name[:3].isdigit() and 350 <= int(p.name[:3]) <= 399
    )
    assert len(queries) == 50, len(queries)
    results = {}
    for path in queries:
        rows = list(graph.query(path.read_text()))
        results[path.name] = rows
        print(f"PASS {path.name} rows={len(rows)}")
    assert len(results["354_missing_assimilation.rq"]) == 1
    assert len(results["355_replay_gap.rq"]) == 1
    assert len(results["357_single_root_risk.rq"]) == 1
    assert len(results["359_return_actuation_violations.rq"]) == 0
    assert len(results["383_independent_alive_consumer_census.rq"]) == 1
    assert len(results["384_unverified_alive_contradiction.rq"]) == 0
    assert len(results["386_ambient_actuation_violation.rq"]) == 0
    assert len(results["397_clean_return_frontier.rq"]) == 1
    assert len(results["398_unresolved_return_opportunities.rq"]) == 1
    shortfall = int(results["399_consumer_replication_1000x_shortfall.rq"][0][0])
    assert shortfall == 9, shortfall
    print("R50_SPARQL_EXECUTION=50 ALIVE shortfall=9")


if __name__ == "__main__":
    main()
