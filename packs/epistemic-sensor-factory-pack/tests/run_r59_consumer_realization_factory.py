#!/usr/bin/env python3
from pathlib import Path
import rdflib

PACK = Path(__file__).resolve().parents[1]
graph = rdflib.Graph()
graph.parse(PACK / "ontology.ttl", format="turtle")
graph.parse(PACK / "fixtures" / "r59-consumer-realization.ttl", format="turtle")
queries = sorted((PACK / "queries").glob("9??_r59_*.rq"))
assert len(queries) == 44, f"expected 44 R59 courts, got {len(queries)}"
rows_by_name = {}
for query in queries:
    rows = list(graph.query(query.read_text()))
    rows_by_name[query.name] = rows
    print(f"{query.name}=PASS rows={len(rows)}")
assert len(rows_by_name["951_r59_realization_plan_count.rq"]) == 1
assert len(rows_by_name["957_r59_rust_cli_realization.rq"]) == 1
assert len(rows_by_name["958_r59_elixir_control_plane_realization.rq"]) == 1
assert len(rows_by_name["959_r59_elixir_process_intelligence_realization.rq"]) == 1
assert len(rows_by_name["960_r59_simulation_gym_realization.rq"]) == 1
for empty_court in (
    "953_r59_missing_target_binding.rq",
    "955_r59_missing_exact_target_head.rq",
    "962_r59_missing_projection_path.rq",
    "964_r59_missing_qualification_command.rq",
    "966_r59_missing_receipt_path.rq",
    "968_r59_missing_replay_path.rq",
    "970_r59_missing_rollback_command.rq",
    "971_r59_standing_inheritance_violations.rq",
    "972_r59_authority_inheritance_violations.rq",
    "974_r59_ambient_do_violations.rq",
    "988_r59_unresolved_plan_gap_count.rq",
    "990_r59_incomplete_realization_plans.rq",
):
    rows = rows_by_name[empty_court]
    if empty_court.endswith("gap_count.rq"):
        assert int(rows[0][0]) == 0, (empty_court, rows)
    else:
        assert rows == [], (empty_court, rows)
assert len(rows_by_name["987_r59_safe_construct_frontier.rq"]) == 4
assert len(rows_by_name["994_r59_prioritized_realization_frontier.rq"]) == 3
projection = list(graph.query((PACK / "queries" / "1010_r59_consumer_realization_projection.rq").read_text()))
assert len(projection) == 4
print("R59_REALIZATION_QUERY_COUNT=44")
print("R59_REALIZATION_PLAN_COUNT=4")
print("R59_PARTIAL_CONSUMER_FRONTIER=3")
print("R59_STANDING_INHERITED=false")
print("R59_AUTHORITY_INHERITED=false")
print("R59_CONSEQUENTIAL_DO=false")
print("R59_CONSUMER_REALIZATION_FACTORY=ALIVE")
