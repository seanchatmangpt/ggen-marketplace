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


def scalar(graph, filename):
    rows = list(graph.query((QUERY_DIR / filename).read_text()))
    if len(rows) != 1 or len(rows[0]) != 1:
        raise AssertionError(f"{filename}: expected one scalar row, got {rows!r}")
    return int(rows[0][0])


def main():
    queries = sorted(QUERY_DIR.glob("6[5-9][1-9]_r55_*.rq")) + sorted(QUERY_DIR.glob("700_r55_*.rq"))
    # The glob above intentionally excludes non-R55 query families; enforce exact numeric range independently.
    queries = sorted(
        p for p in QUERY_DIR.glob("*_r55_*.rq")
        if p.name[:3].isdigit() and 651 <= int(p.name[:3]) <= 700
    )
    if len(queries) != 50:
        print(f"REFUSED[R55_QUERY_CARDINALITY]={len(queries)}")
        return 1

    graph = Graph()
    graph.parse(ONTOLOGY, format="turtle")
    graph.parse(FIXTURE, format="turtle")

    failures = []
    for path in queries:
        try:
            rows = list(graph.query(path.read_text()))
            print(f"{path.name}=PASS rows={len(rows)}")
        except Exception as exc:
            failures.append(f"{path.name}:{type(exc).__name__}:{exc}")

    candidates = set(graph.subjects(RDF.type, ESF.ConsumerAdmissionCandidate))
    exact = {
        c for c in candidates
        if next(graph.objects(c, ESF.candidateHead), None) == next(graph.objects(c, ESF.currentDefaultHead), None)
    }
    no_do = {c for c in candidates if str(next(graph.objects(c, ESF.noAmbientDo), "")).lower() == "true"}

    if len(candidates) != 4:
        failures.append(f"candidate_count:{len(candidates)}!=4")
    if len(exact) != 4:
        failures.append(f"exact_head_count:{len(exact)}!=4")
    if len(no_do) != 4:
        failures.append(f"no_ambient_do_count:{len(no_do)}!=4")
    if scalar(graph, "652_r55_admitted_count.rq") != 3:
        failures.append("admitted_count!=3")
    if scalar(graph, "653_r55_partial_count.rq") != 1:
        failures.append("partial_count!=1")
    if scalar(graph, "655_r55_receipt_return_count.rq") != 2:
        failures.append("receipt_return_count!=2")
    if scalar(graph, "686_r55_strong_readiness_count.rq") != 2:
        failures.append("strong_readiness_count!=2")
    if scalar(graph, "699_r55_independently_ready_shortfall_to_ten.rq") != 9:
        failures.append("independently_ready_shortfall!=9")
    if list(graph.query((QUERY_DIR / "664_r55_ambient_do_violations.rq").read_text())):
        failures.append("ambient_do_violation")

    if failures:
        print("REFUSED[R55_INDEPENDENT_CONSUMER_COURT]=" + " | ".join(failures))
        return 1

    print("R55_QUERY_COUNT=50")
    print("R55_CONSUMER_COUNT=4")
    print("R55_ADMITTED_COUNT=3")
    print("R55_INDEPENDENTLY_READY_COUNT=1")
    print("R55_10X_CONSUMER_SHORTFALL=9")
    print("R55_1000X=NOT_ADMITTED")
    print("R55_INDEPENDENT_CONSUMER_FANOUT=ALIVE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
