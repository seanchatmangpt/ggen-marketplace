#!/usr/bin/env python3
"""Build an evidence-bounded legacy -> canonical consolidation census."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from marketplace import require_admitted
from marketplace_scope import active_pack_names

OWNER_TERMS: dict[str, tuple[str, ...]] = {
    "decision-optionality-pack": (
        "dfcm", "candidate", "option", "opportunity", "selection", "portfolio",
        "errc", "innovation", "capital", "stopping", "counterfactual", "rebloom",
    ),
    "enterprise-governance-pack": (
        "enterprise", "fortune5", "fortune-5", "togaf", "soc2", "certification",
        "assurance", "architecture", "compliance", "control-plane",
    ),
    "evidence-standing-pack": (
        "evidence", "receipt", "standing", "observability", "observation", "provenance",
        "epistemic", "temporal", "replication", "lineage", "affidavit", "witness",
    ),
    "experience-projection-pack": (
        "shadcn", "deckgl", "dashboard", "ui", "ux", "site", "playground", "chrome-ext",
        "layout", "view", "visual", "frontend", "nextjs",
    ),
    "marketplace-governance-pack": (
        "marketplace", "pack-authoring", "pack-maturity", "pack-consolidation", "constitution",
        "admission", "catalog", "manifest", "registry", "commerce",
    ),
    "planning-policy-pack": (
        "planning", "planner", "pddl", "hddl", "htn", "fond", "policy", "scheduler",
        "allocation", "work-selection", "plan-", "planning-federation",
    ),
    "process-intelligence-pack": (
        "ocel", "process", "conformance", "drift", "process-mining", "powL", "powL".lower(),
        "workflow", "event-log", "process-model", "revops",
    ),
    "protocol-integration-pack": (
        "mcp", "a2a", "protocol", "bridge", "adapter", "ffi", "rmcp", "fastmcp",
        "integration", "interop", "transport", "claudecode", "chatgpt",
    ),
    "repository-lifecycle-pack": (
        "repo", "repository", "github", "cargo", "ci", "release", "terraform", "cloud",
        "kubernetes", "k8s", "gcp", "azure", "deployment", "delivery", "toolchain",
    ),
    "semantic-projection-pack": (
        "ggen", "template", "projection", "generation", "generated", "compiler", "factory",
        "fanout", "wasm", "rust", "schema", "ontology", "semantic", "codegen", "self-pack",
    ),
    "state-transition-pack": (
        "runtime", "state", "transition", "remediation", "execution", "actuation", "outcome",
        "autonomic", "control", "rail", "lifecycle", "survivability", "recovery",
    ),
}

DROP_PATTERNS = (
    re.compile(r"(?:^|-)current-run(?:-|$)"),
    re.compile(r"(?:^|-)v\d+(?:-|$)"),
    re.compile(r"(?:^|-)r\d+(?:-|$)"),
    re.compile(r"release-gate$"),
)
FIXTURE_TERMS = ("playground", "interview", "demo", "example", "sample", "starter", "site", "chrome-ext")


def classify_owner(name: str, description: str) -> tuple[str | None, dict[str, int]]:
    text = f"{name} {description}".lower()
    scores = {
        owner: sum(2 if term in name.lower() else 1 for term in terms if term in text)
        for owner, terms in OWNER_TERMS.items()
    }
    best = max(scores.values(), default=0)
    winners = sorted(owner for owner, score in scores.items() if score == best and score > 0)
    return (winners[0] if len(winners) == 1 else None), scores


def disposition(name: str) -> str:
    lowered = name.lower()
    if any(pattern.search(lowered) for pattern in DROP_PATTERNS):
        return "DROP"
    if any(term in lowered for term in FIXTURE_TERMS):
        return "FIXTURE"
    return "ABSORB"


def build_census() -> dict[str, object]:
    packs = sorted(require_admitted(), key=lambda pack: pack.name)
    active = set(active_pack_names())
    rows: list[dict[str, object]] = []
    unresolved: list[str] = []
    for pack in packs:
        if pack.name in active:
            continue
        action = disposition(pack.name)
        owner: str | None = None
        scores: dict[str, int] = {}
        if action != "DROP":
            owner, scores = classify_owner(pack.name, pack.description)
            if owner is None:
                unresolved.append(pack.name)
        rows.append({
            "canonical_owner": owner,
            "description": pack.description,
            "disposition": action,
            "legacy_pack": pack.name,
            "owner_scores": {key: value for key, value in sorted(scores.items()) if value > 0},
            "standing": "CANDIDATE" if action == "DROP" or owner is not None else "UNKNOWN",
            "version": pack.version,
        })
    return {
        "active_count": len(active),
        "legacy_count": len(rows),
        "rows": rows,
        "schema": "https://ggen.dev/marketplace/consolidation-census/v1",
        "unresolved_count": len(unresolved),
        "unresolved_packs": unresolved,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--require-closed", action="store_true")
    args = parser.parse_args()
    payload = build_census()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    if args.require_closed and payload["unresolved_count"]:
        print(f"REFUSED:LEGACY_CENSUS_OPEN:unresolved={payload['unresolved_count']}", file=sys.stderr)
        return 2
    print(
        f"legacy-census active={payload['active_count']} legacy={payload['legacy_count']} unresolved={payload['unresolved_count']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
