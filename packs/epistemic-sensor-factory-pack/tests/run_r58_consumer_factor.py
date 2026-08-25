#!/usr/bin/env python3
import pathlib
import sys
from rdflib import Graph

ROOT = pathlib.Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "epistemic-sensor-factory-pack"
QUERY_DIR = PACK / "queries"
ONTOLOGY = PACK / "ontology.ttl"
FIXTURE = PACK / "fixtures" / "r58-consumer-factor.ttl"

EXPECTED_ROWS = {
    "858_r58_orphan_replication_targets.rq": 0,
    "859_r58_cross_repository_targets.rq": 4,
    "860_r58_replay_verified_receipts.rq": 4,
    "861_r58_unreplayed_receipts.rq": 0,
    "863_r58_single_root_subject_risk.rq": 4,
    "864_r58_receipt_return_capable_candidates.rq": 4,
    "865_r58_receipt_return_gap.rq": 0,
    "866_r58_reusable_court_candidates.rq": 4,
    "867_r58_nonreusable_court_gap.rq": 0,
    "868_r58_ggen_manufacturable_candidates.rq": 4,
    "869_r58_ggen_manufacture_gap.rq": 0,
    "870_r58_public_ontology_aligned_candidates.rq": 4,
    "871_r58_public_ontology_divergence.rq": 0,
    "872_r58_authority_bounded_candidates.rq": 4,
    "873_r58_unbounded_authority_gap.rq": 0,
    "874_r58_no_ambient_do_candidates.rq": 4,
    "875_r58_ambient_do_violation.rq": 0,
    "876_r58_dependency_closed_candidates.rq": 4,
    "877_r58_dependency_open_gap.rq": 0,
    "878_r58_adapter_required_candidates.rq": 3,
    "879_r58_direct_consumer_candidates.rq": 1,
    "881_r58_missing_qualification_path.rq": 0,
    "883_r58_missing_consumer_head.rq": 0,
    "885_r58_default_head_mismatch.rq": 0,
    "887_r58_missing_producer_court_head.rq": 0,
    "891_r58_partial_target_gap.rq": 3,
    "892_r58_returned_alive_standings.rq": 1,
    "893_r58_returned_partial_standings.rq": 3,
    "894_r58_cross_repo_alive_consumers.rq": 1,
    "895_r58_cross_repo_partial_consumers.rq": 3,
    "898_r58_clean_replication_frontier.rq": 1,
    "899_r58_clean_frontier_replay_gap.rq": 0,
    "900_r58_consumer_factor_ten_x_admission.rq": 0,
}

def main() -> int:
    queries = sorted(p for p in QUERY_DIR.glob("*_r58_*.rq") if p.name[:3].isdigit() and 851 <= int(p.name[:3]) <= 900)
    if len(queries) != 50:
        print(f"REFUSED[R58_QUERY_CARDINALITY]={len(queries)}")
        return 1
    graph = Graph()
    graph.parse(ONTOLOGY, format="turtle")
    graph.parse(FIXTURE, format="turtle")
    failures = []
    for path in queries:
        try:
            rows = list(graph.query(path.read_text()))
            print(f"{path.name}=PASS rows={len(rows)}")
            expected = EXPECTED_ROWS.get(path.name)
            if expected is not None and len(rows) != expected:
                failures.append(f"{path.name}:rows={len(rows)}!={expected}")
        except Exception as exc:
            failures.append(f"{path.name}:{type(exc).__name__}:{exc}")
    if failures:
        print("REFUSED[R58_CONSUMER_FACTOR]=" + " | ".join(failures))
        return 1
    print("R58_QUERY_COUNT=50")
    print("R58_EXACT_CONSUMER_SUBJECTS=4")
    print("R58_OBSERVED_ALIVE_CONSUMER_FACTOR=1")
    print("R58_CONSUMER_FACTOR_SHORTFALL=9")
    print("R58_10X_CONSUMER_FACTOR=NOT_ADMITTED")
    print("R58_REFERENCE_ONLY=true")
    print("R58_CONSEQUENTIAL_DO=false")
    print("R58_CONSUMER_FACTOR=ALIVE")
    return 0

if __name__ == "__main__":
    sys.exit(main())
