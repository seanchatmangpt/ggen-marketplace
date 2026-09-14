#!/usr/bin/env python3
from __future__ import annotations

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


def refuse(message: str) -> None:
    print(f"REFUSED:ENTERPRISE_KUDZU_PROFILE: {message}", file=sys.stderr)
    raise SystemExit(2)


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

    print("Enterprise Kudzu profile invariants: PARTIAL_ALIVE")
    print("active_packs=12 front_door=ggen-platform-pack")
    print("closed_loop_observation=true")
    print("dfcm_order=reuse>compose>extend>invent")
    print("human_twin=identity_state_only")
    print("do_authority=external_existing_boundary")


if __name__ == "__main__":
    main()
