#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_ACTIVE_PACKS = {
    "decision-optionality-pack",
    "enterprise-governance-pack",
    "evidence-standing-pack",
    "experience-projection-pack",
    "ggen-platform-pack",
    "marketplace-governance-pack",
    "planning-policy-pack",
    "process-intelligence-pack",
    "protocol-integration-pack",
    "repository-lifecycle-pack",
    "semantic-projection-pack",
    "state-transition-pack",
}

REQUIRED_PROCESS_MARKERS = (
    "pi:ExecutionEpisode",
    "pi:DeclaredBehavior",
    "pi:ObservedBehavior",
    "pi:StablePattern",
    "pi:usesImplementation",
    "pi:ClosedLoopObservation",
)

REQUIRED_DOC_MARKERS = (
    "Capability != Implementation != Provider != Agent != Role != HumanTwin",
    "reuse -> compose -> extend -> invent",
    "C4 — context",
    "FOND policy contract",
    "HDDL decomposition",
    "Human twins in this profile are persistent identity/state objects only.",
    "observed behavior is evidence, not automatic authority",
    "does not grant DO authority",
)

FORBIDDEN_TOP_LEVEL_PACKS = {
    "ash-kudzu-pack",
    "kudzu-pack",
    "genesis-pack",
    "human-twin-pack",
    "a2a-pack",
    "marketplace-intelligence-pack",
}

# --- Real-dependency + adapter convention (v26.9.13) ------------------------
#
# Ontology -> Template -> Real Consumer -> Receipt. Every pr:PriorArtAdapter
# individual that names an ash_* sibling repo is held to a higher bar than
# the generic third-party PriorArtAdapter individuals (GraphQLMesh, Nango,
# Airbyte, ...): it must carry the eight real-dependency/adapter/test RDF
# properties (checked here by text search against enterprise_kudzu.ttl, the
# same lightweight-marker style this script already uses for
# REQUIRED_PROCESS_MARKERS / REQUIRED_DOC_MARKERS) AND a real receipt JSON
# file proving a real `mix test` passed in a real generated consumer.
#
# Receipt path convention (Pilots-phase agents write here):
#   docs/reference/enterprise-kudzu-pilot-receipts/<slug>.json
#
# Receipt JSON required shape:
#   {
#     "individual": "<pr: local name, e.g. AshA2ARuntimeAdapters>",
#     "consumer": "<path or description of the real generated consumer project>",
#     "command": "<real shell command run, must contain 'mix test'>",
#     "exit_code": 0
#   }
# No timestamp field is required or read -- a receipt's validity is about
# the command/exit_code pairing, not when it was captured.

ENTERPRISE_KUDZU_TTL = ROOT / "packs/protocol-integration-pack/enterprise_kudzu.ttl"
PILOT_RECEIPTS_DIR = ROOT / "docs/reference/enterprise-kudzu-pilot-receipts"

REQUIRED_REAL_DEPENDENCY_PROPERTIES = (
    "pr:realDependencyCoordinate",
    "pr:realDependencyApp",
    "pr:adapterModuleName",
    "pr:adapterModulePath",
    "pr:adapterEntrypointModule",
    "pr:adapterEntrypointFunction",
    "pr:adapterTestModuleName",
    "pr:adapterTestPath",
)

# name -> receipt-file slug. Curated, not derived, because a mechanical
# CamelCase->kebab-case transform is ambiguous on names like "AshR2RML" /
# "AshAI" / "AshEx4pm".
ASH_SIBLING_ADAPTERS = {
    "AshA2ARuntimeAdapters": "ash-a2a-runtime-adapters",
    "AshSurfaceAccessibility": "ash-surface-accessibility",
    "AshR2RML": "ash-r2rml",
    "AshAI": "ash-ai",
    "AshExpo": "ash-expo",
    "AshPlanningCenter": "ash-planning-center",
    "AshEx4pm": "ash-ex4pm",
}


def refuse(message: str) -> None:
    print(f"REFUSED:ENTERPRISE_KUDZU_PROFILE: {message}", file=sys.stderr)
    raise SystemExit(2)


def _individual_stanza(ttl_text: str, name: str) -> str:
    """Return the Turtle stanza text for `pr:<name> a pr:PriorArtAdapter ...`,
    from its declaration up to the terminating top-level '.'. Text-based on
    purpose, matching this script's existing marker-search style rather than
    adding an RDF-parser dependency this repo does not otherwise declare."""
    pattern = re.compile(
        r"pr:" + re.escape(name) + r"\s+a\s+pr:PriorArtAdapter\s*;.*?\.\n",
        re.DOTALL,
    )
    match = pattern.search(ttl_text)
    return match.group(0) if match else ""


def check_real_dependency_adapter_convention() -> None:
    if not ENTERPRISE_KUDZU_TTL.exists():
        refuse(f"missing {ENTERPRISE_KUDZU_TTL.relative_to(ROOT)}")
    ttl_text = ENTERPRISE_KUDZU_TTL.read_text()

    missing_individuals = [
        name for name in ASH_SIBLING_ADAPTERS if f"pr:{name} a pr:PriorArtAdapter" not in ttl_text
    ]
    if missing_individuals:
        refuse(f"ash_* sibling adapters not declared in enterprise_kudzu.ttl: {missing_individuals}")

    problems: list[str] = []
    for name, slug in ASH_SIBLING_ADAPTERS.items():
        stanza = _individual_stanza(ttl_text, name)
        missing_props = [
            prop for prop in REQUIRED_REAL_DEPENDENCY_PROPERTIES if prop not in stanza
        ]
        if missing_props:
            problems.append(
                f"pr:{name}: missing real-dependency properties {missing_props} "
                f"(PENDING -- Pilots phase has not admitted real facts yet)"
            )
            continue

        receipt_path = PILOT_RECEIPTS_DIR / f"{slug}.json"
        if not receipt_path.exists():
            problems.append(
                f"pr:{name}: real-dependency properties present but no receipt at "
                f"{receipt_path.relative_to(ROOT)} (PENDING -- Pilots phase has not run yet)"
            )
            continue

        try:
            receipt = json.loads(receipt_path.read_text())
        except json.JSONDecodeError as exc:
            problems.append(f"pr:{name}: receipt {receipt_path.relative_to(ROOT)} is not valid JSON: {exc}")
            continue

        receipt_problems = []
        if receipt.get("individual") != name:
            receipt_problems.append(f"individual field {receipt.get('individual')!r} != {name!r}")
        if "mix test" not in str(receipt.get("command", "")):
            receipt_problems.append("command field does not contain 'mix test'")
        if receipt.get("exit_code") != 0:
            receipt_problems.append(f"exit_code {receipt.get('exit_code')!r} != 0")
        if not receipt.get("consumer"):
            receipt_problems.append("consumer field missing/empty")

        if receipt_problems:
            problems.append(
                f"pr:{name}: receipt {receipt_path.relative_to(ROOT)} invalid: {receipt_problems}"
            )

    if problems:
        refuse("real-dependency+adapter convention not yet satisfied for all ash_* siblings: " + " | ".join(problems))


def main() -> None:
    manifest = tomllib.loads((ROOT / "marketplace.active.toml").read_text())
    active = manifest["active"]
    packs = set(active["packs"])

    if active["front_door"] != "ggen-platform-pack":
        refuse(f"unexpected front door: {active['front_door']!r}")
    if len(active["packs"]) != 12:
        refuse(f"active pack cardinality changed: {len(active['packs'])}")
    if packs != EXPECTED_ACTIVE_PACKS:
        refuse(
            "active topology drift; "
            f"missing={sorted(EXPECTED_ACTIVE_PACKS - packs)} "
            f"extra={sorted(packs - EXPECTED_ACTIVE_PACKS)}"
        )

    present_forbidden = sorted(
        name for name in FORBIDDEN_TOP_LEVEL_PACKS if (ROOT / "packs" / name).exists()
    )
    if present_forbidden:
        refuse(f"profiles must compose existing authorities, not create packs: {present_forbidden}")

    process_text = (ROOT / "packs/process-intelligence-pack/ontology.ttl").read_text()
    missing_process = [m for m in REQUIRED_PROCESS_MARKERS if m not in process_text]
    if missing_process:
        refuse(f"process-intelligence profile missing markers: {missing_process}")

    doc = ROOT / "docs/reference/enterprise-kudzu-v26.9.13.md"
    if not doc.exists():
        refuse("production contract document missing")
    doc_text = doc.read_text()
    missing_doc = [m for m in REQUIRED_DOC_MARKERS if m not in doc_text]
    if missing_doc:
        refuse(f"production contract missing markers: {missing_doc}")

    # Human twin semantics in this profile are identity/state only. The profile
    # must not encode automated personnel or employment decisions.
    prohibited_doc_terms = (
        "automatic hiring decision",
        "automatic firing decision",
        "automatic compensation decision",
    )
    found = [term for term in prohibited_doc_terms if term in doc_text.lower()]
    if found:
        refuse(f"human-status decision semantics are out of scope: {found}")

    check_real_dependency_adapter_convention()

    print("Enterprise Kudzu profile invariants: PARTIAL_ALIVE")
    print("active_packs=12 front_door=ggen-platform-pack")
    print("closed_loop_observation=true")
    print("dfcm_order=reuse>compose>extend>invent")
    print("human_twin=identity_state_only")
    print("do_authority=external_existing_boundary")


if __name__ == "__main__":
    main()
