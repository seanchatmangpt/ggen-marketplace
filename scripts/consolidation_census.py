#!/usr/bin/env python3
"""Build an evidence-bounded legacy -> canonical consolidation census.

Adapted from a reference script authored on an unmerged branch
(consolidation_census_ref.py), which was designed against a
`marketplace.active.toml` file and a different set of 12 skeleton pack
names that never landed on `main`. This version is adapted for the 12
REAL canonical packs merged on `main` as of 2026-09-12 (see issue #439):

  marketplace-governance-pack, evidence-standing-pack,
  decision-optionality-pack, semantic-projection-pack,
  planning-policy-pack, process-intelligence-pack, state-transition-pack,
  protocol-integration-pack, repository-lifecycle-pack,
  enterprise-governance-pack, experience-projection-pack,
  ggen-platform-pack

Adaptation choice: the reference script read the active-pack set from
`marketplace_scope.active_pack_names()`, which in turn read
`marketplace.active.toml`. Neither the module nor the TOML file exists on
`main`. Rather than fabricate a `marketplace.active.toml` file that has no
other consumer and no admitted schema on this branch, this script defines
the 12 real active pack names as a plain Python constant
(`ACTIVE_PACK_NAMES`) below -- this is the smaller, more honest diff: one
new script file with an inline, auditable constant, instead of a new
config file + loader module + constant, none of which anything else on
`main` reads.

This script is investigation/classification ONLY. It does not delete,
move, or modify any pack directory. See docs/reference/
legacy-pack-census-26.9.12.json for the last committed run's output and
the accompanying PR for the qualifying statement required by issue #439:
no legacy pack has been retired or modified as a result of running this
census.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from marketplace import require_admitted  # noqa: E402

# The 12 canonical packs merged into `main` per issue #439 (2026-09-12).
# Legacy packs matching one of these names by exact directory/pack name
# are excluded from the census -- they *are* canonical, not candidates
# for absorption into a canonical pack.
ACTIVE_PACK_NAMES: tuple[str, ...] = (
    "marketplace-governance-pack",
    "evidence-standing-pack",
    "decision-optionality-pack",
    "semantic-projection-pack",
    "planning-policy-pack",
    "process-intelligence-pack",
    "state-transition-pack",
    "protocol-integration-pack",
    "repository-lifecycle-pack",
    "enterprise-governance-pack",
    "experience-projection-pack",
    "ggen-platform-pack",
)

# Real generation-equivalence findings (2026-09-14), NOT re-derivable from
# OWNER_TERMS scoring -- classify_owner()/disposition() below are a keyword
# heuristic over pack.name/description only; they cannot see actual RDF
# vocabulary or generated-artifact shape. These 11 rows were checked for
# real equivalence (read both packs' pack.toml/ontology.ttl/templates/gates
# in full, compared RDF classes/properties and generated-output shape,
# checked for live consumer references) and every one REFUTED: the
# canonical_owner the heuristic assigned shares no real ontology vocabulary
# or generated-artifact shape with the legacy pack -- the ABSORB guess
# rested on description-text word overlap (e.g. "MCP"/"protocol") only.
# See docs/reference/legacy-pack-census-26.9.12.json's "verification_note"
# for the full methodology statement. Keyed by legacy_pack name; value is
# (verified_disposition, verified_reason). Applied in build_census() so a
# future re-run of this script does not silently regress these findings
# back to unverified CANDIDATE standing.
VERIFIED_OVERRIDES: dict[str, tuple[str, str]] = {
    "autofde-lab-mcp-surface-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "No shared ontology vocabulary, no shared template output shape (Rust MCP "
        "tool surface + JSON tool list vs Elixir Adapter/Capability/Protocol/"
        "Transport bindings). ABSORB guess rests on naming similarity "
        "(\"MCP\"/\"protocol\") only. If retirable at all, the real candidate is "
        "gym-mcp-surface-pack (stated byte-identical consumer), not "
        "protocol-integration-pack -- untested by this pass.",
    ),
    "chatgptgym-gymact-bridge-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "No shared class (sosa:Procedure vs pi:Capability/Adapter/Protocol/"
        "Transport), no shared property, no shared template output language "
        "(Rust vs Elixir). Also has real registry dependents (mcp-protocol family "
        "list, verify-gym-packs.py's fixed 4-pack manifest) that would need "
        "migration even if a real target existed.",
    ),
    "claudecode-gymact-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "No shared ontology vocabulary or generated-artifact shape (Rust "
        "operation-catalog constants vs Elixir adapter modules). Naming-"
        "similarity ABSORB guess.",
    ),
    "elixir-mcp-a2a-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "No shared ontology vocabulary (ema:CapabilitySurface/Capability vs "
        "pi:Capability/Adapter/Protocol/Transport) or template targets "
        "(AshAi.Mcp.Router/A2A.Agent modules vs thin adapter/mix-dep-install "
        "modules).",
    ),
    "fastmcp-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "No shared ontology vocabulary (fmcp:Server/Tool vs pi:Protocol/Transport/"
        "Capability/Adapter) or output shape (single Python FastMCP server file "
        "vs Elixir Mix adapters).",
    ),
    "gdmcp-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "No shared domain: gdmcp models the MCP wire-protocol spec itself across "
        "10 SDK languages; protocol-integration-pack models an abstract "
        "capability-to-protocol-binding convention for Elixir consumers. Zero "
        "ontology/template overlap.",
    ),
    "gym-mcp-surface-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "No shared ontology vocabulary or output shape (gym-agnostic "
        "sosa:Procedure -> Rust tool catalog vs pi:Capability/Adapter -> Elixir "
        "adapters).",
    ),
    "portable-consequence-protocol-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "Domain is a runtime authority/receipt/replay conformance protocol with "
        "an executable Python reference witness (odrl/prov/earl-based); "
        "protocol-integration-pack has no authority/consequence/receipt/replay "
        "concept anywhere. Zero real overlap.",
    ),
    "rmcp-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "Models one specific Rust crate's (rmcp) trait/macro/transport/feature "
        "surface; protocol-integration-pack models an abstract cross-protocol "
        "capability-reuse convention generating Elixir artifacts. Zero ontology/"
        "template overlap.",
    ),
    "speedrun-talent-network-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "Manufactures a full typed Rust REST/MCP API-client crate for one named "
        "external building block; protocol-integration-pack generates Elixir "
        "Mix-dependency adapters. Zero domain overlap.",
    ),
    "planning-federation-pack": (
        "REFUTED_NOT_EQUIVALENT",
        "Is itself a real RDF-to-Python planning-compiler (6 real generation "
        "rules -> planner IR/catalog/symbolic/interchange/binary/projector). "
        "planning-policy-pack is a semantic-only vocabulary pack (HDDL/FOND "
        "terms, SELECT!=DO gate, no query->template->output pipeline at all). "
        "Absorbing would delete planning-federation-pack's entire real "
        "generation capability with no replacement.",
    ),
}

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
        "ocel", "process", "conformance", "drift", "process-mining", "powl",
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
    "ggen-platform-pack": (
        "platform", "clap-noun-verb", "clap", "cli-", "-cli", "sdk", "runtime-platform",
        "core-platform", "infra-platform",
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
    active = set(ACTIVE_PACK_NAMES)
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
        row: dict[str, object] = {
            "canonical_owner": owner,
            "description": pack.description,
            "disposition": action,
            "legacy_pack": pack.name,
            "owner_scores": {key: value for key, value in sorted(scores.items()) if value > 0},
            "standing": "CANDIDATE" if action == "DROP" or owner is not None else "UNKNOWN",
            "version": pack.version,
        }
        override = VERIFIED_OVERRIDES.get(pack.name)
        if override is not None:
            verified_disposition, verified_reason = override
            row["verified_disposition"] = verified_disposition
            row["verified_reason"] = verified_reason
            # A real, checked REFUTED overrides the heuristic's unverified
            # CANDIDATE standing -- see VERIFIED_OVERRIDES' module comment.
            row["standing"] = "REFUTED"
        rows.append(row)
    return {
        "active_count": len(active),
        "active_packs": sorted(active),
        "legacy_count": len(rows),
        "rows": rows,
        "schema": "https://ggen.dev/marketplace/consolidation-census/v1",
        "issue": "https://github.com/seanchatmangpt/ggen-marketplace/issues/439",
        "note": (
            "Investigation/classification only. No legacy pack has been "
            "retired, moved, or modified as a result of this census."
        ),
        "unresolved_count": len(unresolved),
        "unresolved_packs": unresolved,
        "verification_note": (
            "2026-09-14: Real generation-equivalence check (not naming-similarity) "
            "run against all 11 legacy_pack rows owned by "
            "canonical_owner=protocol-integration-pack (10 rows) and "
            "canonical_owner=planning-policy-pack (1 row) -- the two most "
            "tractable-looking canonical packs (protocol-integration-pack already "
            "had real templates; planning-policy-pack had only 1 mapped legacy "
            "pack). Method: read both packs' pack.toml/ontology.ttl/templates/"
            "gates in full, compare RDF vocabulary and generated-artifact shape, "
            "check for live consumer references. Result: 11/11 REFUTED -- every "
            "mapping was a naming-similarity artifact (shared words like "
            "\"MCP\"/\"protocol\" in the description) with zero shared ontology "
            "class/property or generated-output shape. This does not refute the "
            "whole census (289 rows remain unchecked) but is strong evidence the "
            "canonical_owner field (computed from owner_scores, a weighted "
            "keyword heuristic) should not be treated as a verified absorption "
            "target without the same per-row check applied here. See "
            "VERIFIED_OVERRIDES in this script for the durable record (survives "
            "re-running this script) and each row's verified_disposition/"
            "verified_reason for the specific evidence."
        ),
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
