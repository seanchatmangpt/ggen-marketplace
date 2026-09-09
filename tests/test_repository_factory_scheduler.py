from __future__ import annotations

import importlib.util
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "packs" / "repository-factory-scheduler-pack" / "gates" / "schedule.py"
POLICY_PATH = ROOT / "packs" / "repository-factory-scheduler-pack" / "policy.toml"
spec = importlib.util.spec_from_file_location("repository_factory_scheduler", MODULE_PATH)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def policy(target: int = 2, capacity: int = 4):
    value = module.load_policy(POLICY_PATH)
    value = deepcopy(value)
    value["factory"]["target_repositories"] = target
    value["factory"]["candidate_capacity"] = capacity
    value["factory"]["reserve_repositories"] = capacity - target
    return value


def candidate(repo: str, work: str, impact=50, independence=50, reversibility=50, cost=50):
    return {
        "repository": repo,
        "head_sha": "a" * 40,
        "candidate": {
            "id": work,
            "admitted": True,
            "impact": impact,
            "independence": independence,
            "reversibility": reversibility,
            "cost": cost,
            "acceptance": "exact verifier exits zero",
            "verifier": {"available": True, "command": f"verify {work}"},
        },
    }


def payload(repositories):
    return {
        "schema": module.INPUT_SCHEMA,
        "run_id": "2026-08-20",
        "repositories": repositories,
    }


def test_selects_highest_ranked_candidates():
    result = module.schedule(
        payload([
            candidate("o/low", "low", impact=10),
            candidate("o/high", "high", impact=90),
            candidate("o/mid", "mid", impact=50),
        ]),
        policy(target=2, capacity=4),
    )
    assert [x["repository"] for x in result["selections"]] == ["o/high", "o/mid"]
    assert result["planned_commits"] == 6


def test_no_work_is_preserved_not_selected():
    result = module.schedule(payload([{"repository": "o/idle", "head_sha": "b" * 40, "candidate": None}]), policy(1, 2))
    assert result["standing"] == "BLOCKED"
    assert result["no_work"] == [{"repository": "o/idle", "code": "NO_WORK"}]
    assert result["planned_commits"] == 0


def test_missing_exact_head_is_blocked():
    item = candidate("o/repo", "work")
    item["head_sha"] = "main"
    result = module.schedule(payload([item]), policy(1, 2))
    assert result["blocked"] == [{"repository": "o/repo", "code": "BLOCKED_EXACT_HEAD_REQUIRED"}]


def test_unadmitted_work_is_refused():
    item = candidate("o/repo", "work")
    item["candidate"]["admitted"] = False
    result = module.schedule(payload([item]), policy(1, 2))
    assert result["refusals"] == [{"repository": "o/repo", "code": "REFUSED_UNADMITTED_WORK"}]


def test_verifier_is_mandatory():
    item = candidate("o/repo", "work")
    item["candidate"]["verifier"]["available"] = False
    result = module.schedule(payload([item]), policy(1, 2))
    assert result["blocked"] == [{"repository": "o/repo", "code": "BLOCKED_VERIFIER_REQUIRED"}]


def test_exact_three_commit_cycle_and_order():
    result = module.schedule(payload([candidate("o/repo", "otel")]), policy(1, 2))
    plan = result["selections"][0]["commit_plan"]
    assert [step["phase"] for step in plan] == ["OBSERVE", "CONSTRUCT", "VERIFY"]
    assert len(plan) == 3


def test_scheduler_has_no_do_authority():
    result = module.schedule(payload([candidate("o/repo", "work")]), policy(1, 2))
    assert result["authority"] == {"do_authority": False, "claim_ceiling": "PLAN_ONLY"}
    assert result["receipt"]["do_authority"] is False


def test_input_order_does_not_change_receipt_or_selection():
    items = [candidate("o/a", "a", impact=70), candidate("o/b", "b", impact=80)]
    first = module.schedule(payload(items), policy(2, 4))
    second = module.schedule(payload(list(reversed(items))), policy(2, 4))
    assert first["input_digest"] == second["input_digest"]
    assert first["receipt"]["digest"] == second["receipt"]["digest"]
    assert [x["repository"] for x in first["selections"]] == [x["repository"] for x in second["selections"]]


def test_cost_is_ascending_after_equal_higher_priority_scores():
    result = module.schedule(
        payload([candidate("o/expensive", "x", cost=90), candidate("o/cheap", "c", cost=10)]),
        policy(2, 4),
    )
    assert [x["repository"] for x in result["selections"]] == ["o/cheap", "o/expensive"]


def test_duplicate_repository_is_refused():
    result = module.schedule(payload([candidate("o/repo", "a"), candidate("o/repo", "b")]), policy(2, 4))
    assert {x["code"] for x in result["refusals"]} == {"REFUSED_DUPLICATE_REPOSITORY"}
    assert result["selected_repositories"] == 1


def test_target_capacity_shortfall_is_explicit():
    result = module.schedule(payload([candidate("o/repo", "work")]), policy(2, 4))
    assert result["standing"] == "PARTIAL_ALIVE"
    assert "TARGET_CAPACITY_SHORTFALL" in result["blockers"]


def test_score_out_of_range_is_refused():
    result = module.schedule(payload([candidate("o/repo", "work", impact=101)]), policy(1, 2))
    assert result["refusals"] == [{"repository": "o/repo", "code": "REFUSED_IMPACT_OUT_OF_RANGE"}]


def test_default_policy_encodes_180_by_3_with_20_slack():
    value = module.load_policy(POLICY_PATH)
    assert value["factory"] == {
        "target_repositories": 180,
        "commits_per_repository": 3,
        "candidate_capacity": 200,
        "reserve_repositories": 20,
    }


def test_receipt_is_deterministic():
    data = payload([candidate("o/repo", "work")])
    first = module.schedule(deepcopy(data), policy(1, 2))
    second = module.schedule(deepcopy(data), policy(1, 2))
    assert first["receipt"]["digest"] == second["receipt"]["digest"]
