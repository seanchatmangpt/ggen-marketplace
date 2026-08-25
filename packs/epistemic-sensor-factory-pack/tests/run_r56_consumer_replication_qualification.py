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


def main():
    queries = sorted(
        p for p in QUERY_DIR.glob("*_r56_*.rq")
        if p.name[:3].isdigit() and 701 <= int(p.name[:3]) <= 750
    )
    if len(queries) != 50:
        print(f"REFUSED[R56_QUERY_CARDINALITY]={len(queries)}")
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
    if len(rows(graph, "701_r56_exact_head_parity.rq")) != 4:
        failures.append("exact_head_parity!=4")
    if rows(graph, "702_r56_stale_head_refusal.rq"):
        failures.append("stale_head_present")
    if len(rows(graph, "705_r56_receipt_return_ready.rq")) != 2:
        failures.append("receipt_return_ready!=2")
    if len(rows(graph, "709_r56_ggen_manufacturable.rq")) != 2:
        failures.append("ggen_manufacturable!=2")
    if len(rows(graph, "721_r56_admitted_consumers.rq")) != 3:
        failures.append("admitted_consumers!=3")
    if len(rows(graph, "722_r56_partial_consumers.rq")) != 1:
        failures.append("partial_consumers!=1")
    if len(rows(graph, "729_r56_full_replication_ready.rq")) != 2:
        failures.append("full_replication_ready!=2")
    if rows(graph, "716_r56_ambient_do_violation.rq"):
        failures.append("ambient_do_violation")

    if failures:
        print("REFUSED[R56_CONSUMER_REPLICATION_QUALIFICATION]=" + " | ".join(failures))
        return 1

    print("R56_QUERY_COUNT=50")
    print("R56_CONSUMER_COUNT=4")
    print("R56_FULL_REPLICATION_READY=2")
    print("R56_10X_CONSUMER_SHORTFALL=8")
    print("R56_1000X=NOT_ADMITTED")
    print("R56_CONSUMER_REPLICATION_QUALIFICATION=ALIVE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
