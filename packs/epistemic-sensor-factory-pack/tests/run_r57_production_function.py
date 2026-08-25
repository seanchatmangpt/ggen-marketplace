#!/usr/bin/env python3
import pathlib
import sys
from rdflib import Graph

ROOT = pathlib.Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "epistemic-sensor-factory-pack"
QUERY_DIR = PACK / "queries"
ONTOLOGY = PACK / "ontology.ttl"
FIXTURE = PACK / "fixtures" / "r57-production-function.ttl"

EXPECTED_ROWS = {
    "759_r57_product_factor_consistency.rq": 0,
    "762_r57_single_root_multiplier_risk.rq": 0,
    "763_r57_multi_root_multiplier_admission.rq": 1,
    "766_r57_positive_frontier_delta.rq": 1,
    "767_r57_nonexpanding_frontier.rq": 0,
    "773_r57_1000x_candidates.rq": 1,
    "774_r57_1000x_shortfall.rq": 0,
    "775_r57_all_factors_ge_10.rq": 1,
    "776_r57_observation_factor_below_10.rq": 0,
    "777_r57_reuse_factor_below_10.rq": 0,
    "778_r57_opportunity_factor_below_10.rq": 0,
    "780_r57_exact_subject_missing_receipt.rq": 0,
    "788_r57_unreplayed_receipts.rq": 0,
    "792_r57_dependency_relief_gap.rq": 0,
    "794_r57_low_causal_confidence.rq": 0,
    "796_r57_high_propagation_latency.rq": 0,
    "798_r57_zero_fanout_observations.rq": 0,
    "799_r57_authority_safe_multiplier_subjects.rq": 3,
    "800_r57_clean_1000x_frontier.rq": 1,
}

def main() -> int:
    queries = sorted(p for p in QUERY_DIR.glob("*_r57_*.rq") if p.name[:3].isdigit() and 751 <= int(p.name[:3]) <= 800)
    if len(queries) != 50:
        print(f"REFUSED[R57_QUERY_CARDINALITY]={len(queries)}")
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
        print("REFUSED[R57_PRODUCTION_FUNCTION]=" + " | ".join(failures))
        return 1
    print("R57_QUERY_COUNT=50")
    print("R57_OBSERVATION_FACTOR=10")
    print("R57_REUSE_FACTOR=10")
    print("R57_OPPORTUNITY_FACTOR=10")
    print("R57_REFERENCE_PRODUCT=1000")
    print("R57_REFERENCE_ONLY=true")
    print("R57_CONSEQUENTIAL_DO=false")
    print("R57_PRODUCTION_FUNCTION=ALIVE")
    return 0

if __name__ == "__main__":
    sys.exit(main())
