#!/usr/bin/env python3
"""Deterministic, CONSTRUCT-only repository factory scheduler.

The scheduler never writes repositories. It admits candidate work against exact
heads, preserves NO_WORK, ranks eligible candidates, and emits a three-commit
OBSERVE -> CONSTRUCT -> VERIFY plan plus a deterministic planning receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

INPUT_SCHEMA = "https://ggen.dev/marketplace/repository-factory/input/v1"
PLAN_SCHEMA = "https://ggen.dev/marketplace/repository-factory/plan/v1"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
DEFAULT_POLICY = Path(__file__).resolve().parents[1] / "policy.toml"
PHASES = ("OBSERVE", "CONSTRUCT", "VERIFY")


def canonical_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def normalized_input(payload: dict[str, Any]) -> dict[str, Any]:
    clone = dict(payload)
    repos = payload.get("repositories", [])
    if isinstance(repos, list):
        clone["repositories"] = sorted(
            repos,
            key=lambda item: (
                item.get("repository", "") if isinstance(item, dict) else "",
                item.get("candidate", {}).get("id", "")
                if isinstance(item, dict) and isinstance(item.get("candidate"), dict)
                else "",
            ),
        )
    return clone


def load_policy(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        policy = tomllib.load(handle)
    factory = policy.get("factory")
    selection = policy.get("selection")
    authority = policy.get("authority")
    if not isinstance(factory, dict) or not isinstance(selection, dict) or not isinstance(authority, dict):
        raise ValueError("REFUSED_POLICY_TABLE_MISSING")
    if factory.get("commits_per_repository") != 3:
        raise ValueError("REFUSED_THREE_COMMIT_LAW")
    if authority.get("do_authority") is not False:
        raise ValueError("REFUSED_AMBIENT_DO_AUTHORITY")
    target = factory.get("target_repositories")
    capacity = factory.get("candidate_capacity")
    reserve = factory.get("reserve_repositories")
    if not all(isinstance(v, int) and v >= 0 for v in (target, capacity, reserve)):
        raise ValueError("REFUSED_POLICY_CARDINALITY_INVALID")
    if target > capacity or reserve != capacity - target:
        raise ValueError("REFUSED_POLICY_SLACK_INCONSISTENT")
    return policy


def _candidate_disposition(
    item: dict[str, Any], score_min: int, score_max: int
) -> tuple[str, str | None, dict[str, Any] | None]:
    repository = item.get("repository")
    if not isinstance(repository, str) or not repository.strip():
        return "REFUSED", "REFUSED_REPOSITORY_IDENTITY_MISSING", None
    candidate = item.get("candidate")
    if candidate is None or candidate == {}:
        return "NO_WORK", "NO_WORK", None
    if not isinstance(candidate, dict):
        return "REFUSED", "REFUSED_CANDIDATE_INVALID", None
    if candidate.get("status") == "NO_WORK":
        return "NO_WORK", "NO_WORK", None
    head_sha = item.get("head_sha")
    if not isinstance(head_sha, str) or not SHA40.fullmatch(head_sha):
        return "BLOCKED", "BLOCKED_EXACT_HEAD_REQUIRED", None
    work_id = candidate.get("id")
    if not isinstance(work_id, str) or not work_id.strip():
        return "REFUSED", "REFUSED_WORK_ID_MISSING", None
    if candidate.get("admitted") is not True:
        return "REFUSED", "REFUSED_UNADMITTED_WORK", None
    verifier = candidate.get("verifier")
    if not isinstance(verifier, dict) or verifier.get("available") is not True:
        return "BLOCKED", "BLOCKED_VERIFIER_REQUIRED", None
    command = verifier.get("command")
    acceptance = candidate.get("acceptance")
    if not isinstance(command, str) or not command.strip() or not isinstance(acceptance, str) or not acceptance.strip():
        return "BLOCKED", "BLOCKED_VERIFIER_OR_ACCEPTANCE_MISSING", None
    scores: dict[str, int] = {}
    for key in ("impact", "independence", "reversibility", "cost"):
        value = candidate.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or not score_min <= value <= score_max:
            return "REFUSED", f"REFUSED_{key.upper()}_OUT_OF_RANGE", None
        scores[key] = value
    admitted = {
        "repository": repository,
        "head_sha": head_sha,
        "work_id": work_id,
        "impact": scores["impact"],
        "independence": scores["independence"],
        "reversibility": scores["reversibility"],
        "cost": scores["cost"],
        "verifier": command,
        "acceptance": acceptance,
    }
    return "ELIGIBLE", None, admitted


def _rank_key(candidate: dict[str, Any]) -> tuple[Any, ...]:
    return (
        -candidate["impact"],
        -candidate["independence"],
        -candidate["reversibility"],
        candidate["cost"],
        candidate["repository"],
        candidate["work_id"],
    )


def _commit_plan(candidate: dict[str, Any]) -> list[dict[str, str]]:
    work_id = candidate["work_id"]
    return [
        {
            "ordinal": "1",
            "phase": "OBSERVE",
            "subject": f"spec({work_id}): admit {work_id}",
            "proof": "ontology/schema/fixture/acceptance criterion",
        },
        {
            "ordinal": "2",
            "phase": "CONSTRUCT",
            "subject": f"feat({work_id}): construct {work_id}",
            "proof": "implementation/generator/adapter/integration",
        },
        {
            "ordinal": "3",
            "phase": "VERIFY",
            "subject": f"test({work_id}): verify {work_id}",
            "proof": candidate["verifier"],
        },
    ]


def schedule(payload: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    refusals: list[dict[str, str]] = []
    blocked: list[dict[str, str]] = []
    no_work: list[dict[str, str]] = []
    eligible: list[dict[str, Any]] = []

    if payload.get("schema") != INPUT_SCHEMA:
        refusals.append({"repository": "<run>", "code": "REFUSED_SCHEMA_MISMATCH"})
    repositories = payload.get("repositories")
    if not isinstance(repositories, list):
        repositories = []
        refusals.append({"repository": "<run>", "code": "REFUSED_REPOSITORIES_NOT_ARRAY"})

    selection = policy["selection"]
    score_min = selection["score_min"]
    score_max = selection["score_max"]
    if not isinstance(score_min, int) or not isinstance(score_max, int) or score_min > score_max:
        raise ValueError("REFUSED_POLICY_SCORE_RANGE_INVALID")

    seen: set[str] = set()
    for item in repositories:
        if not isinstance(item, dict):
            refusals.append({"repository": "<invalid>", "code": "REFUSED_REPOSITORY_ENTRY_INVALID"})
            continue
        repository = item.get("repository") if isinstance(item.get("repository"), str) else "<invalid>"
        if repository in seen and repository != "<invalid>":
            refusals.append({"repository": repository, "code": "REFUSED_DUPLICATE_REPOSITORY"})
            continue
        seen.add(repository)
        disposition, code, admitted = _candidate_disposition(item, score_min, score_max)
        if disposition == "ELIGIBLE" and admitted is not None:
            eligible.append(admitted)
        elif disposition == "NO_WORK":
            no_work.append({"repository": repository, "code": code or "NO_WORK"})
        elif disposition == "BLOCKED":
            blocked.append({"repository": repository, "code": code or "BLOCKED"})
        else:
            refusals.append({"repository": repository, "code": code or "REFUSED"})

    target = policy["factory"]["target_repositories"]
    eligible.sort(key=_rank_key)
    selected = eligible[:target]
    overflow = eligible[target:]

    selections = []
    for candidate in selected:
        plan = _commit_plan(candidate)
        assert tuple(step["phase"] for step in plan) == PHASES
        selections.append(
            {
                **candidate,
                "disposition": "SELECTED",
                "commit_plan": plan,
            }
        )

    blockers: list[str] = []
    if len(selected) < target:
        blockers.append("TARGET_CAPACITY_SHORTFALL")
    if not selected:
        blockers.append("NO_ELIGIBLE_REPOSITORIES")

    factory = policy["factory"]
    result: dict[str, Any] = {
        "schema": PLAN_SCHEMA,
        "standing": "BLOCKED" if not selected else "PARTIAL_ALIVE",
        "run_id": payload.get("run_id"),
        "authority": {"do_authority": False, "claim_ceiling": "PLAN_ONLY"},
        "target_repositories": target,
        "commits_per_repository": factory["commits_per_repository"],
        "candidate_capacity": factory["candidate_capacity"],
        "reserve_repositories": factory["reserve_repositories"],
        "selected_repositories": len(selected),
        "planned_commits": len(selected) * factory["commits_per_repository"],
        "eligible_overflow": [c["repository"] for c in overflow],
        "selections": selections,
        "no_work": sorted(no_work, key=lambda x: x["repository"]),
        "blocked": sorted(blocked, key=lambda x: (x["repository"], x["code"])),
        "refusals": sorted(refusals, key=lambda x: (x["repository"], x["code"])),
        "blockers": blockers,
        "input_digest": canonical_digest(normalized_input(payload)),
        "policy_digest": canonical_digest(policy),
    }
    receipt_subject = {k: v for k, v in result.items() if k != "receipt"}
    result["receipt"] = {
        "kind": "repository_factory_planning_receipt",
        "digest": canonical_digest(receipt_subject),
        "selected_repositories": len(selected),
        "planned_commits": result["planned_commits"],
        "do_authority": False,
    }
    return result


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("REFUSED_INPUT_ROOT_NOT_OBJECT")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    args = parser.parse_args(argv)
    try:
        policy = load_policy(args.policy)
        result = schedule(load_json(args.input), policy)
    except (OSError, json.JSONDecodeError, tomllib.TOMLDecodeError, ValueError) as exc:
        result = {
            "schema": PLAN_SCHEMA,
            "standing": "BLOCKED",
            "authority": {"do_authority": False, "claim_ceiling": "PLAN_ONLY"},
            "refusals": [{"repository": "<run>", "code": str(exc)}],
        }
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result.get("standing") == "PARTIAL_ALIVE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
