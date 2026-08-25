#!/usr/bin/env python3
import pathlib
import sys

from rdflib import Graph, Namespace, RDF

ROOT = pathlib.Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "epistemic-sensor-factory-pack"
QUERY_DIR = PACK / "queries"
FIXTURE = PACK / "fixtures" / "r55-independent-consumer-fanout.ttl"
ONTOLOGY = PACK / "ontology.ttl"
ESF = Namespace("https://ggen.dev/ontology/epistemic-sensor-factory#")


def rows(graph, filename):
    return list(graph.query((QUERY_DIR / filename).read_text()))


def scalar(graph, filename):
    result = rows(graph, filename)
    if len(result) != 1 or len(result[0]) != 1:
        raise ValueError(f"{filename}: expected one scalar row, got {result!r}")
    return int(result[0][0])


def main():
    queries = sorted(
        p for p in QUERY_DIR.glob("*_r57_*.rq")
        if p.name[:3].isdigit() and 751 <= int(p.name[:3]) <= 800
    )
    if len(queries) != 50:
        print(f"REFUSED[R57_QUERY_CARDINALITY]={len(queries)}")
        return 1

    graph = Graph()
    graph.parse(ONTOLOGY, format="turtle")
    graph.parse(FIXTURE, format="turtle")

    failures = []
    for path in queries:
        try:
            result = list(graph.query(path.read_text()))
            print(f"{path.name}=PASS rows={len(result)}")
        except Exception as exc:
            failures.append(f"{path.name}:{type(exc).__name__}:{exc}")

    candidates = set(graph.subjects(RDF.type, ESF.ConsumerAdmissionCandidate))
    if len(candidates) != 4:
        failures.append(f"candidate_count:{len(candidates)}!=4")
    if len(rows(graph, "751_r57_adapter_required_candidates.rq")) != 4:
        failures.append("adapter_required_candidates!=4")
    if len(rows(graph, "754_r57_full_ready_adapter_candidates.rq")) != 2:
        failures.append("full_ready_adapter_candidates!=2")
    if len(rows(graph, "755_r57_adapter_receipt_gap.rq")) != 2:
        failures.append("adapter_receipt_gap!=2")
    if len(rows(graph, "756_r57_adapter_manufacture_gap.rq")) != 2:
        failures.append("adapter_manufacture_gap!=2")
    if len(rows(graph, "757_r57_adapter_dependency_gap.rq")) != 2:
        failures.append("adapter_dependency_gap!=2")
    if len(rows(graph, "758_r57_adapter_projection_gap.rq")) != 2:
        failures.append("adapter_projection_gap!=2")
    if rows(graph, "768_r57_adapter_stale_head.rq"):
        failures.append("stale_head_present")
    if scalar(graph, "773_r57_adapter_consumer_family_count.rq") != 4:
        failures.append("consumer_family_count!=4")
    if scalar(graph, "774_r57_partial_adapter_count.rq") != 1:
        failures.append("partial_adapter_count!=1")
    if scalar(graph, "775_r57_admitted_adapter_count.rq") != 3:
        failures.append("admitted_adapter_count!=3")
    if scalar(graph, "782_r57_full_adapter_readiness_count.rq") != 2:
        failures.append("full_adapter_readiness_count!=2")
    if scalar(graph, "783_r57_full_readiness_shortfall_to_ten.rq") != 8:
        failures.append("full_readiness_shortfall!=8")
    if rows(graph, "792_r57_missing_target_binding.rq"):
        failures.append("missing_target_binding")
    if rows(graph, "793_r57_missing_qualification_path.rq"):
        failures.append("missing_qualification_path")
    if len(rows(graph, "799_r57_prioritized_adapter_candidate.rq")) != 1:
        failures.append("prioritized_adapter_candidate!=1")
    if len(rows(graph, "800_r57_clean_adapter_capital_frontier.rq")) != 4:
        failures.append("clean_adapter_capital_frontier!=4")

    if failures:
        print("REFUSED[R57_CONSUMER_ADAPTER_CAPITAL]=" + " | ".join(failures))
        return 1

    print("R57_QUERY_COUNT=50")
    print("R57_CONSUMER_COUNT=4")
    print("R57_CONSUMER_FAMILIES=4")
    print("R57_FULL_ADAPTER_READY=2")
    print("R57_ADAPTER_GAP_CONSUMERS=2")
    print("R57_10X_CONSUMER_SHORTFALL=8")
    print("R57_1000X=NOT_ADMITTED")
    print("R57_CONSUMER_ADAPTER_CAPITAL=ALIVE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
