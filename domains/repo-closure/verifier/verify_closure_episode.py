#!/usr/bin/env python3.11
"""Independent episode verifier for repo-closure@v26.9.13.

Verifies that an MX episode adheres to mx-episode-schema@v26.9.13 and binds
the exact CalVer identities required for replay:
  Replay = f(SubjectHead, Pattern@v26.9.13, Domain@v26.9.13, HDDL@v26.9.13,
             FOND@v26.9.13, Verifier@v26.9.13)
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any


EXPECTED_CALVER = "v26.9.13"
REQUIRED_FIELDS = {
    "episode_id",
    "subject_repo",
    "subject_head",
    "pattern_version",
    "domain_version",
    "hddl_version",
    "fond_version",
    "verifier_version",
    "selected_decomposition",
    "observed_transitions",
    "cost_score",
    "receipt_hash",
    "resulting_standing",
}


@dataclass(frozen=True)
class VerificationResult:
    valid: bool
    code: str
    message: str


def verify_episode(data: dict[str, Any]) -> VerificationResult:
    missing = REQUIRED_FIELDS - set(data.keys())
    if missing:
        return VerificationResult(
            valid=False,
            code="MISSING_EPISODE_FIELDS",
            message=f"Missing required fields: {sorted(missing)}",
        )

    # Check CalVer bindings
    for field in ("pattern_version", "domain_version", "hddl_version", "fond_version", "verifier_version"):
        val = data.get(field)
        if val != EXPECTED_CALVER:
            return VerificationResult(
                valid=False,
                code="CALVER_MISMATCH",
                message=f"Expected {field}='{EXPECTED_CALVER}', found '{val}'",
            )

    standing = data.get("resulting_standing")
    if standing not in {"ALIVE", "PARTIAL_ALIVE", "BLOCKED", "BUILD_BROKEN", "UNSUPPORTED"}:
        return VerificationResult(
            valid=False,
            code="INVALID_STANDING",
            message=f"Resulting standing '{standing}' is not recognized",
        )

    return VerificationResult(valid=True, code="VALID", message="Episode lawfully verified and bound for replay")


def main() -> int:
    sample_episode = {
        "episode_id": "MXEpisode/2026-09-13/000001",
        "subject_repo": "seanchatmangpt/ash_pplan",
        "subject_head": "00f14b1b966900aa129f16a2e51727ef697823ec",
        "pattern_version": "v26.9.13",
        "domain_version": "v26.9.13",
        "hddl_version": "v26.9.13",
        "fond_version": "v26.9.13",
        "verifier_version": "v26.9.13",
        "selected_decomposition": ["task_regenerate", "task_compile", "task_inspect", "task_emit_receipt"],
        "observed_transitions": [{"step": "compile", "outcome": "pass"}],
        "cost_score": 1.2,
        "receipt_hash": "sha256:920b3868d75bdf0bed6abcb1422d29f7e785d945c43d11af6e0f455bfd4299cf",
        "resulting_standing": "ALIVE",
    }

    result = verify_episode(sample_episode)
    print(f"[{result.code}] {result.message}")
    return 0 if result.valid else 1


if __name__ == "__main__":
    sys.exit(main())
