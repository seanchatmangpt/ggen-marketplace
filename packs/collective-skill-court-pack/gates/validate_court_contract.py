#!/usr/bin/env python3
"""Fail-closed verifier for the generated collective-skill court contract."""

from __future__ import annotations

import json
import pathlib
import sys

EXPECTED_SCHEMA = "collective-skill-court.v1"
EXPECTED_AUTHORITY = "OBSERVE|SELECT|CONSTRUCT"
REQUIRED_FLAGS = {
    "source_provenance",
    "exact_marketplace_pin",
    "exact_subject_pin",
    "replay_identity",
    "oracle_pass",
    "noop_fail",
    "mutation_rejection",
}


def main(path: str) -> int:
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != EXPECTED_SCHEMA:
        print("REFUSED[SCHEMA_IDENTITY]")
        return 2
    if data.get("authority_ceiling") != EXPECTED_AUTHORITY:
        print("REFUSED[AUTHORITY_CEILING]")
        return 3
    if data.get("grants_do_authority") is not False:
        print("REFUSED[AMBIENT_DO_AUTHORITY]")
        return 4
    projections = data.get("projections")
    if not isinstance(projections, dict):
        print("REFUSED[MISSING_PROJECTIONS]")
        return 5
    if projections.get("sjira_work_order") != "urn:seanchatmangpt:sjira:v1#WorkOrder":
        print("REFUSED[SJIRA_PROJECTION]")
        return 6
    if projections.get("sa2a_candidate") != "https://spec.autofde.org/sa2a#Candidate":
        print("REFUSED[SA2A_PROJECTION]")
        return 7
    required = data.get("requires")
    if not isinstance(required, dict) or set(required) != REQUIRED_FLAGS:
        print("REFUSED[REQUIREMENT_SET]")
        return 8
    if not all(required.values()):
        print("REFUSED[WEAKENED_REQUIREMENT]")
        return 9
    print("ALIVE: collective-skill court contract is fail-closed and construct-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
