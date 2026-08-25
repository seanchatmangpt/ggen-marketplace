#!/usr/bin/env python3
import pathlib
import sys
from rdflib import Graph

ROOT = pathlib.Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "epistemic-sensor-factory-pack"
QUERY_DIR = PACK / "queries"
ONTOLOGY = PACK / "ontology.ttl"
FIXTURE = PACK / "fixtures" / "r57-production-function.ttl"

CANONICAL = [
"751_r57_production_function_observation_count.rq","752_r57_observation_factor_count.rq","753_r57_reuse_factor_count.rq","754_r57_opportunity_factor_count.rq","755_r57_multiplicative_product.rq","756_r57_missing_observation_factor.rq","757_r57_missing_reuse_factor.rq","758_r57_missing_opportunity_factor.rq","759_r57_product_factor_consistency.rq","760_r57_factor_evidence_count.rq","761_r57_factor_independent_roots.rq","762_r57_single_root_multiplier_risk.rq","763_r57_multi_root_multiplier_admission.rq","764_r57_frontier_before.rq","765_r57_frontier_after.rq","766_r57_positive_frontier_delta.rq","767_r57_nonexpanding_frontier.rq","768_r57_portfolio_subject_count.rq","769_r57_reused_capability_count.rq","770_r57_downstream_opportunity_count.rq","771_r57_multiplier_admitted.rq","772_r57_multiplier_not_admitted.rq","773_r57_1000x_candidates.rq","774_r57_1000x_shortfall.rq","775_r57_all_factors_ge_10.rq","776_r57_observation_factor_below_10.rq","777_r57_reuse_factor_below_10.rq","778_r57_opportunity_factor_below_10.rq","779_r57_exact_subject_receipt_count.rq","780_r57_exact_subject_missing_receipt.rq","781_r57_cross_repository_target_count.rq","782_r57_admitted_target_count.rq","783_r57_partial_target_count.rq","784_r57_alive_consumer_standing_count.rq","785_r57_partial_consumer_standing_count.rq","786_r57_returned_receipt_count.rq","787_r57_replay_verified_receipts.rq","788_r57_unreplayed_receipts.rq","789_r57_evidence_root_diversity.rq","790_r57_evidence_root_concentration.rq","791_r57_realized_dependency_relief.rq","792_r57_dependency_relief_gap.rq","793_r57_high_causal_confidence.rq","794_r57_low_causal_confidence.rq","795_r57_propagation_latency.rq","796_r57_high_propagation_latency.rq","797_r57_fanout_distribution.rq","798_r57_zero_fanout_observations.rq","799_r57_authority_safe_multiplier_subjects.rq","800_r57_clean_1000x_frontier.rq"]
EXPECTED_ROWS = {"759_r57_product_factor_consistency.rq":0,"762_r57_single_root_multiplier_risk.rq":0,"763_r57_multi_root_multiplier_admission.rq":1,"766_r57_positive_frontier_delta.rq":1,"767_r57_nonexpanding_frontier.rq":0,"773_r57_1000x_candidates.rq":1,"774_r57_1000x_shortfall.rq":0,"775_r57_all_factors_ge_10.rq":1,"776_r57_observation_factor_below_10.rq":0,"777_r57_reuse_factor_below_10.rq":0,"778_r57_opportunity_factor_below_10.rq":0,"780_r57_exact_subject_missing_receipt.rq":0,"788_r57_unreplayed_receipts.rq":0,"792_r57_dependency_relief_gap.rq":0,"794_r57_low_causal_confidence.rq":0,"796_r57_high_propagation_latency.rq":0,"798_r57_zero_fanout_observations.rq":0,"799_r57_authority_safe_multiplier_subjects.rq":3,"800_r57_clean_1000x_frontier.rq":1}

def main() -> int:
    queries = [QUERY_DIR / name for name in CANONICAL]
    missing = [p.name for p in queries if not p.is_file()]
    if missing:
        print("REFUSED[R57_CANONICAL_SENSOR_MISSING]=" + ",".join(missing)); return 1
    graph = Graph(); graph.parse(ONTOLOGY, format="turtle"); graph.parse(FIXTURE, format="turtle")
    failures=[]
    for path in queries:
        try:
            rows=list(graph.query(path.read_text())); print(f"{path.name}=PASS rows={len(rows)}")
            expected=EXPECTED_ROWS.get(path.name)
            if expected is not None and len(rows)!=expected: failures.append(f"{path.name}:rows={len(rows)}!={expected}")
        except Exception as exc: failures.append(f"{path.name}:{type(exc).__name__}:{exc}")
    if failures:
        print("REFUSED[R57_PRODUCTION_FUNCTION]="+" | ".join(failures)); return 1
    print("R57_QUERY_COUNT=50\nR57_REFERENCE_PRODUCT=1000\nR57_REFERENCE_ONLY=true\nR57_CONSEQUENTIAL_DO=false\nR57_PRODUCTION_FUNCTION=ALIVE")
    return 0
if __name__ == "__main__": sys.exit(main())
