#!/usr/bin/env python3
from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "r52-consumer-admission-current.ttl"


def main():
    graph = Graph()
    graph.parse(ROOT / "ontology.ttl", format="turtle")
    graph.parse(FIXTURE, format="turtle")
    queries = []
    for path in sorted((ROOT / "queries").glob("*.rq")):
        prefix = path.name.split("_", 1)[0]
        if prefix.isdigit() and (451 <= int(prefix) <= 499 or int(prefix) == 600):
            queries.append(path)
    assert len(queries) == 50, len(queries)
    results = {}
    for path in queries:
        rows = list(graph.query(path.read_text()))
        results[path.name] = rows
        print(f"PASS {path.name} rows={len(rows)}")
    assert int(results["451_admission_candidate_count.rq"][0][0]) == 4
    assert len(results["465_missing_receipt_return_capability.rq"]) == 2
    assert len(results["466_missing_ggen_manufacturability.rq"]) == 2
    assert len(results["467_missing_dependency_closure.rq"]) == 2
    assert int(results["468_exact_head_parity_count.rq"][0][0]) == 4
    assert int(results["469_admitted_target_count.rq"][0][0]) == 2
    assert len(results["481_candidate_without_admitted_target.rq"]) == 2
    assert int(results["495_independently_ready_count.rq"][0][0]) == 2
    assert int(results["496_independent_readiness_shortfall.rq"][0][0]) == 8
    assert len(results["499_clean_admission_realization_frontier.rq"]) == 2
    print("R52_ADMISSION_REALIZATION=50 ALIVE independently_ready=2 shortfall=8")


if __name__ == "__main__":
    main()
