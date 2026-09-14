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

REQUIRED_MARKERS = {
    "packs/decision-optionality-pack/ontology.ttl": (
        "do:MinimumNoveltyLaw",
        "do:Reuse",
        "do:Compose",
        "do:Extend",
        "do:Invent",
        "do:requiresPriorArtClosure true",
        "do:requiresFalsifier true",
    ),
    "packs/semantic-projection-pack/ontology.ttl": (
        "sp:MachineSemanticCompilation",
        "sp:HyperSearch",
        "sp:EquivalenceCheck",
        "sp:CapabilityClosure",
        "sp:Residualize",
        "sp:humanImplementationRequired false",
        "sp:grantsDoAuthority false",
    ),
    "packs/experience-projection-pack/ontology.ttl": (
        "xp:MachineExperienceProfile",
        "xp:machineDiscoverable true",
        "xp:formalSemantics true",
        "xp:composable true",
        "xp:verifiable true",
        "xp:repairable true",
        "xp:replayable true",
        "xp:authorityExplicit true",
        "xp:requiresHumanInterpretation false",
    ),
    "packs/marketplace-governance-pack/ontology.ttl": (
        "mg:MinimumNoveltyAdmissionLaw",
        "mg:requiresPriorArtClosure true",
        "mg:requiresResidualFalsifier true",
        "mg:grantsDoAuthority false",
    ),
    "packs/ggen-platform-pack/source.ttl": (
        "g:MachineSemanticCompilationProfile",
        "do:MinimumNoveltyLaw",
        "sp:MachineSemanticCompilation",
        "xp:MachineExperienceProfile",
        "mg:MinimumNoveltyAdmissionLaw",
        "g:grantsDoAuthority false",
    ),
}


def refuse(message: str) -> None:
    print(f"REFUSED:MSCT_PROFILE_INVARIANT: {message}", file=sys.stderr)
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
        missing = sorted(EXPECTED_ACTIVE_PACKS - packs)
        extra = sorted(packs - EXPECTED_ACTIVE_PACKS)
        refuse(f"active topology drift; missing={missing} extra={extra}")

    forbidden_pack_dirs = (
        ROOT / "packs" / "msct-pack",
        ROOT / "packs" / "machine-experience-pack",
    )
    existing_forbidden = [str(path.relative_to(ROOT)) for path in forbidden_pack_dirs if path.exists()]
    if existing_forbidden:
        refuse(f"MSCT/MX must compose existing authorities, not add top-level packs: {existing_forbidden}")

    for relative_path, markers in REQUIRED_MARKERS.items():
        text = (ROOT / relative_path).read_text()
        missing = [marker for marker in markers if marker not in text]
        if missing:
            refuse(f"{relative_path} missing markers: {missing}")

    decision = (ROOT / "packs/decision-optionality-pack/ontology.ttl").read_text()
    ordered_modes = (
        ("do:Reuse", "do:selectionOrder 1"),
        ("do:Compose", "do:selectionOrder 2"),
        ("do:Extend", "do:selectionOrder 3"),
        ("do:Invent", "do:selectionOrder 4"),
    )
    cursor = -1
    for mode, order in ordered_modes:
        mode_pos = decision.find(mode, cursor + 1)
        order_pos = decision.find(order, mode_pos)
        if mode_pos < 0 or order_pos < 0:
            refuse(f"minimum-novelty ordering not encoded for {mode}")
        cursor = order_pos

    print("MSCT/MX profile invariants: ALIVE")
    print("active_packs=12 front_door=ggen-platform-pack")
    print("minimum_novelty=reuse>compose>extend>invent")
    print("human_implementation_required=false grants_do_authority=false")


if __name__ == "__main__":
    main()
