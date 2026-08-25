#!/usr/bin/env python3
import pathlib
import sys

from rdflib import Graph

ROOT = pathlib.Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "epistemic-sensor-factory-pack"
QUERY_DIR = PACK / "queries"
FIXTURE = PACK / "fixtures" / "r55-independent-consumer-fanout.ttl"
ONTOLOGY = PACK / "ontology.ttl"

EXPECTED_SCALARS = {
    "701_r56_pair_count.rq": 6,
    "702_r56_cross_family_pair_count.rq": 6,
    "703_r56_same_family_pair_count.rq": 0,
    "704_r56_both_identity_verified_pairs.rq": 6,
    "705_r56_identity_gap_pairs.rq": 0,
    "706_r56_both_authority_bounded_pairs.rq": 6,
    "707_r56_authority_gap_pairs.rq": 0,
    "708_r56_both_receipt_return_pairs.rq": 1,
    "709_r56_receipt_bridge_pairs.rq": 4,
    "710_r56_both_ggen_manufacturable_pairs.rq": 1,
    "711_r56_manufacturability_bridge_pairs.rq": 4,
    "712_r56_both_dependency_closed_pairs.rq": 1,
    "713_r56_dependency_closure_bridge_pairs.rq": 4,
    "714_r56_both_replay_capable_pairs.rq": 6,
    "715_r56_replay_gap_pairs.rq": 0,
    "716_r56_both_no_ambient_do_pairs.rq": 6,
    "717_r56_ambient_do_pair_violations.rq": 0,
    "718_r56_both_public_ontology_pairs.rq": 6,
    "719_r56_public_ontology_gap_pairs.rq": 0,
    "720_r56_both_projection_capable_pairs.rq": 1,
    "721_r56_projection_bridge_pairs.rq": 4,
    "722_r56_both_court_reusable_pairs.rq": 6,
    "723_r56_reusable_court_gap_pairs.rq": 0,
    "724_r56_exact_head_pairs.rq": 6,
    "725_r56_stale_head_pair_count.rq": 0,
    "726_r56_both_admitted_pairs.rq": 3,
    "727_r56_admitted_partial_pairs.rq": 3,
    "728_r56_qualification_path_diversity_pairs.rq": 6,
    "729_r56_shared_qualification_path_pairs.rq": 0,
    "730_r56_both_adapter_required_pairs.rq": 6,
    "731_r56_adapter_mixed_pairs.rq": 0,
    "732_r56_adapter_free_pairs.rq": 0,
    "733_r56_cross_repository_pairs.rq": 6,
    "734_r56_consumer_triple_count.rq": 4,
    "735_r56_cross_family_triples.rq": 4,
    "736_r56_fully_identity_verified_triples.rq": 4,
    "737_r56_fully_authority_bounded_triples.rq": 4,
    "738_r56_fully_receipt_return_triples.rq": 0,
    "739_r56_fully_ggen_manufacturable_triples.rq": 0,
    "740_r56_fully_dependency_closed_triples.rq": 0,
    "741_r56_fully_replay_capable_triples.rq": 4,
    "742_r56_fully_no_ambient_do_triples.rq": 4,
    "743_r56_fully_public_ontology_triples.rq": 4,
    "744_r56_fully_projection_capable_triples.rq": 0,
    "745_r56_fully_court_reusable_triples.rq": 4,
    "746_r56_fully_exact_head_triples.rq": 4,
    "747_r56_fully_admitted_triples.rq": 1,
    "748_r56_adapter_free_triples.rq": 0,
    "749_r56_triples_with_partial_member.rq": 3,
}
CLEAN_FRONTIER = "750_r56_clean_combinatorial_frontier.rq"
R56_COMBINATORIAL_QUERY_NAMES = tuple(EXPECTED_SCALARS) + (CLEAN_FRONTIER,)


def main():
    queries = [QUERY_DIR / name for name in R56_COMBINATORIAL_QUERY_NAMES]
    missing = [path.name for path in queries if not path.is_file()]
    if len(queries) != 50 or missing:
        print(f"REFUSED[R56_COMBINATORIAL_QUERY_CONTRACT]=count:{len(queries)} missing:{missing}")
        return 1

    graph = Graph()
    graph.parse(ONTOLOGY, format="turtle")
    graph.parse(FIXTURE, format="turtle")
    failures = []

    for path in queries:
        try:
            rows = list(graph.query(path.read_text()))
            print(f"{path.name}=PASS rows={len(rows)}")
            if path.name in EXPECTED_SCALARS:
                if len(rows) != 1 or len(rows[0]) != 1:
                    failures.append(f"{path.name}:expected scalar row")
                elif int(rows[0][0]) != EXPECTED_SCALARS[path.name]:
                    failures.append(f"{path.name}:{int(rows[0][0])}!={EXPECTED_SCALARS[path.name]}")
            elif path.name == CLEAN_FRONTIER and len(rows) != 1:
                failures.append(f"{path.name}:rows={len(rows)}!=1")
        except Exception as exc:
            failures.append(f"{path.name}:{type(exc).__name__}:{exc}")

    if failures:
        print("REFUSED[R56_COMBINATORIAL_PORTFOLIO]=" + " | ".join(failures))
        return 1

    print("R56_QUERY_COUNT=50")
    print("R56_PAIR_COUNT=6")
    print("R56_TRIPLE_COUNT=4")
    print("R56_CLEAN_COMBINATORIAL_FRONTIER=1")
    print("R56_CONSEQUENTIAL_DO=false")
    print("R56_COMBINATORIAL_CONSUMER_PORTFOLIO=ALIVE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
