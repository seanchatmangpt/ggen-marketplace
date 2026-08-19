#!/usr/bin/env python3
"""Independent stdlib court for challenger-value/1.

This witness validates claim standing and deterministic presentation. It has no
network access, no customer/outcome discovery authority, and no consequential DO.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ALLOWED_AUDIENCES = {
    "cio-cto", "ciso", "cfo", "platform", "fortune5-buyer", "hiring-manager"
}
ALLOWED_KINDS = {"OBSERVED", "VERIFIED", "INFERRED", "HYPOTHESIS"}
PHASE_KIND = {
    "TEACH": {"OBSERVED", "VERIFIED"},
    "REFRAME": {"INFERRED", "HYPOTHESIS", "VERIFIED"},
    "RATIONAL_IMPACT": {"HYPOTHESIS", "VERIFIED"},
    "NEW_WAY": {"OBSERVED", "VERIFIED", "INFERRED"},
    "PROOF": {"VERIFIED"},
}
DIAGNOSTICS = {
    "cio-cto": "Can you trace one AI-generated production change from exact input through independent acceptance evidence and replay?",
    "ciso": "Which controls are mechanically outside your agents' authority to change?",
    "cfo": "Can you separate AI construction savings from the human verification cost created downstream?",
    "platform": "Which platform invariants are generated from canonical semantics rather than synchronized by hand?",
    "fortune5-buyer": "Which coordination steps could disappear if constraints, evidence, and handoffs were executable?",
    "hiring-manager": "How do you evaluate engineers who operate software factories rather than manually author every artifact?",
}


class Refusal(ValueError):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"REFUSED:{code}: {detail}")


def canonical_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _validate_claim(claim: dict[str, Any]) -> None:
    phase = str(claim.get("phase", ""))
    kind = str(claim.get("kind", ""))
    text = str(claim.get("text", "")).strip()
    if phase not in PHASE_KIND:
        raise Refusal("UNSUPPORTED_PHASE", phase)
    if kind not in ALLOWED_KINDS or kind not in PHASE_KIND[phase]:
        raise Refusal("UNSUPPORTED_CLAIM", f"{phase} cannot use {kind}")
    if not text:
        raise Refusal("EMPTY_CLAIM", phase)
    if claim.get("metric") and not claim.get("source"):
        raise Refusal("METRIC_WITHOUT_SOURCE", phase)
    if phase == "PROOF":
        if not claim.get("source"):
            raise Refusal("PROOF_WITHOUT_SOURCE", text)
        exact = str(claim.get("exact_subject", ""))
        if len(exact) != 40 or any(ch not in "0123456789abcdef" for ch in exact.lower()):
            raise Refusal("PROOF_WITHOUT_EXACT_SUBJECT", text)
        if claim.get("standing") == "ALIVE" and claim.get("standing_evidence") is not True:
            raise Refusal("ALIVE_WITHOUT_STANDING", text)
    if claim.get("customer_outcome") and kind != "VERIFIED":
        raise Refusal("OUTCOME_AS_FACT", text)


def compile_brief(case: dict[str, Any]) -> dict[str, Any]:
    audience = str(case.get("audience", ""))
    if audience not in ALLOWED_AUDIENCES:
        raise Refusal("UNSUPPORTED_AUDIENCE", audience)
    claims = list(case.get("claims") or [])
    if not claims:
        raise Refusal("NO_CLAIMS", "at least one admitted claim is required")
    for claim in claims:
        _validate_claim(claim)

    by_phase: dict[str, list[dict[str, Any]]] = {phase: [] for phase in PHASE_KIND}
    for claim in claims:
        by_phase[claim["phase"]].append(claim)
    for required in ("TEACH", "REFRAME", "RATIONAL_IMPACT", "NEW_WAY", "PROOF"):
        if not by_phase[required]:
            raise Refusal("MISSING_PHASE", required)

    # Preserve alternatives: claims within each phase remain visible rather than
    # being destructively collapsed by a model. The first item is only a
    # deterministic reversible presentation recommendation.
    frontier = {
        phase: sorted(items, key=lambda c: (canonical_digest(c), c["text"]))
        for phase, items in by_phase.items()
    }
    selected = {phase: items[0] for phase, items in frontier.items()}

    brief = {
        "protocol": "challenger-value/1",
        "audience": audience,
        "teach": selected["TEACH"]["text"],
        "reframe": selected["REFRAME"]["text"],
        "rational_impact": selected["RATIONAL_IMPACT"]["text"],
        "new_way": selected["NEW_WAY"]["text"],
        "proof": selected["PROOF"]["text"],
        "take_control": DIAGNOSTICS[audience],
        "frontier": frontier,
        "irreversible_selections": 0,
        "actuation": False,
    }
    brief["receipt_sha256"] = canonical_digest(brief)
    return brief


def run_vectors(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    passed = 0
    for vector in payload["vectors"]:
        try:
            result = compile_brief(vector["case"])
        except Refusal as exc:
            if vector["expect"].get("refusal") != exc.code:
                raise AssertionError(f"{vector['id']}: got {exc.code}") from exc
        else:
            if vector["expect"].get("status") != "ADMITTED":
                raise AssertionError(f"{vector['id']}: unexpectedly admitted")
            replay = compile_brief(vector["case"])
            assert result == replay, vector["id"]
            assert result["actuation"] is False
            assert result["irreversible_selections"] == 0
            assert len(result["receipt_sha256"]) == 64
        passed += 1
    print(json.dumps({"standing": "ADMITTED", "vectors_passed": passed}, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--vectors",
        type=Path,
        default=Path(__file__).parents[2] / "vectors" / "conformance.json",
    )
    args = parser.parse_args()
    return run_vectors(args.vectors)


if __name__ == "__main__":
    raise SystemExit(main())
