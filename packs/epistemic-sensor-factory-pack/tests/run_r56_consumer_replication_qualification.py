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

R56_REPLICATION_QUERY_NAMES = (
    "701_r56_exact_head_parity.rq",
    "702_r56_stale_head_refusal.rq",
    "703_r56_bounded_authority.rq",
    "704_r56_unbounded_authority_refusal.rq",
    "705_r56_receipt_return_ready.rq",
    "706_r56_missing_receipt_return.rq",
    "707_r56_public_ontology_alignment.rq",
    "708_r56_private_schema_refusal.rq",
    "709_r56_ggen_manufacturable.rq",
    "710_r56_nonmanufacturable_consumer.rq",
    "711_r56_replay_capable.rq",
    "712_r56_replay_gap.rq",
    "713_r56_dependency_closed.rq",
    "714_r56_dependency_open.rq",
    "715_r56_no_ambient_do.rq",
    "716_r56_ambient_do_violation.rq",
    "717_r56_generated_projection_ready.rq",
    "718_r56_generated_projection_gap.rq",
    "719_r56_adapter_required.rq",
    "720_r56_adapterless_consumers.rq",
    "721_r56_admitted_consumers.rq",
    "722_r56_partial_consumers.rq",
    "723_r56_target_token_bound.rq",
    "724_r56_qualification_path_bound.rq",
    "725_r56_consumer_family_projection.rq",
    "726_r56_candidate_count.rq",
    "727_r56_admitted_count.rq",
    "728_r56_partial_count.rq",
    "729_r56_full_replication_ready.rq",
    "730_r56_ready_without_admission.rq",
    "731_r56_admitted_without_receipt_return.rq",
    "732_r56_admitted_without_manufacture.rq",
    "733_r56_admitted_without_dependency_closure.rq",
    "734_r56_admitted_without_projection.rq",
    "735_r56_partial_with_return_capability.rq",
    "736_r56_partial_with_manufacture.rq",
    "737_r56_partial_dependency_closed.rq",
    "738_r56_partial_projection_ready.rq",
    "739_r56_return_and_manufacture_ready.rq",
    "740_r56_return_manufacture_replay.rq",
    "741_r56_dependency_projection_closure.rq",
    "742_r56_safe_manufacture_ready.rq",
    "743_r56_safe_return_ready.rq",
    "744_r56_adapter_burden_frontier.rq",
    "745_r56_manufacture_gap_frontier.rq",
    "746_r56_receipt_gap_frontier.rq",
    "747_r56_dependency_gap_frontier.rq",
    "748_r56_projection_gap_frontier.rq",
    "749_r56_next_partial_consumer.rq",
    "750_r56_clean_replication_frontier.rq",
)


def rows(graph, filename):
    return list(graph.query((QUERY_DIR / filename).read_text()))


def main():
    queries = [QUERY_DIR / name for name in R56_REPLICATION_QUERY_NAMES]
    missing = [path.name for path in queries if not path.is_file()]
    if len(queries) != 50 or missing:
        print(f"REFUSED[R56_QUERY_CONTRACT]=count:{len(queries)} missing:{missing}")
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
