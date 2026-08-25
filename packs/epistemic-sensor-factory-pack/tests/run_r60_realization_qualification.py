#!/usr/bin/env python3
from pathlib import Path
import rdflib

PACK = Path(__file__).resolve().parents[1]
graph = rdflib.Graph()
graph.parse(PACK / "ontology.ttl", format="turtle")
graph.parse(PACK / "fixtures" / "r59-consumer-realization.ttl", format="turtle")
queries = sorted((PACK / "queries").glob("10??_r60_*.rq")) + sorted((PACK / "queries").glob("1100_r60_*.rq"))
assert len(queries) == 50, f"expected 50 R60 courts, got {len(queries)}"
rows_by_name = {}
for query in queries:
    rows = list(graph.query(query.read_text()))
    rows_by_name[query.name] = rows
    print(f"{query.name}=PASS rows={len(rows)}")

for empty_court in (
    "1055_r60_unbound_plan_falsifier.rq",
    "1056_r60_missing_exact_head_falsifier.rq",
    "1057_r60_invalid_sha_length_falsifier.rq",
    "1058_r60_duplicate_exact_head_falsifier.rq",
    "1065_r60_candidates_without_plan.rq",
    "1066_r60_orphan_plans.rq",
    "1073_r60_candidates_missing_target.rq",
    "1076_r60_multiple_plans_per_candidate_falsifier.rq",
    "1078_r60_path_completeness_falsifier.rq",
    "1086_r60_unsafe_realization_falsifier.rq",
    "1088_r60_nonready_manufacturing_standing.rq",
    "1089_r60_standing_inheritance_falsifier.rq",
    "1090_r60_authority_inheritance_falsifier.rq",
):
    assert rows_by_name[empty_court] == [], (empty_court, rows_by_name[empty_court])

assert int(rows_by_name["1095_r60_distinct_artifact_families.rq"][0][0]) == 4
assert int(rows_by_name["1096_r60_complete_plan_shortfall_to_ten.rq"][0][0]) == 6
assert int(rows_by_name["1097_r60_alive_plan_shortfall_to_ten.rq"][0][0]) == 9
assert len(rows_by_name["1098_r60_adapter_required_frontier.rq"]) == 3
assert len(rows_by_name["1099_r60_safe_realization_frontier.rq"]) == 4
assert int(rows_by_name["1100_r60_realization_qualification_crown.rq"][0][0]) == 4
print("R60_QUERY_COUNT=50")
print("R60_COMPLETE_PLAN_COUNT=4")
print("R60_ALIVE_CONSUMER_COUNT=1")
print("R60_SHORTFALL_TO_TEN=9")
print("R60_CONSEQUENTIAL_DO=false")
print("R60_REALIZATION_QUALIFICATION=ALIVE")
