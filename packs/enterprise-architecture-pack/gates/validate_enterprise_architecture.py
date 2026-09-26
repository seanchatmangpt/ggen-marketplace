#!/usr/bin/env python3
"""Fail-closed DfCM Industry Closure ABB/SBB qualification gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

LEVEL = {"NONE": 0, "OBSERVE": 1, "SELECT": 2, "CONSTRUCT": 3, "DO": 4}


def canonical_digest(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def qualify(graph: dict) -> dict:
    refusals: list[dict] = []
    receipts: list[dict] = []

    if graph.get("schema") != "ggen.ea.graph.v1":
        refusals.append({"code": "UNSUPPORTED_SCHEMA", "subject": graph.get("schema")})

    abbs = {item["id"]: item for item in graph.get("abbs", [])}
    contracts = {item["id"]: item for item in graph.get("contracts", [])}
    candidates = {item["id"]: item for item in graph.get("candidate_sbbs", [])}
    packs = {item["id"] for item in graph.get("packs", [])}

    identities = [set(abbs), set(candidates), packs]
    if any(identities[i] & identities[j] for i in range(3) for j in range(i + 1, 3)):
        refusals.append({"code": "TYPE_CONFLATION", "subject": "ABB/SBB/PACK"})

    qualifications = {}
    for qualification in graph.get("qualifications", []):
        qualifications.setdefault(qualification["sbb"], []).append(qualification)

    for candidate_id, candidate in sorted(candidates.items()):
        local: list[str] = []
        abb = abbs.get(candidate.get("abb"))
        if abb is None:
            local.append("UNKNOWN_ABB")
            contract = None
        else:
            contract = contracts.get(abb.get("contract"))
            if contract is None:
                local.append("UNKNOWN_CONTRACT")

        if candidate.get("digest") in (None, ""):
            local.append("UNKNOWN_IDENTITY")
        if candidate.get("mutable") is not False:
            local.append("MUTABLE_SUBJECT")

        candidate_authority = LEVEL.get(candidate.get("authority"))
        ceiling = LEVEL.get(contract.get("authority_ceiling")) if contract else None
        if candidate_authority is None or ceiling is None:
            local.append("UNKNOWN_AUTHORITY")
        elif candidate_authority > ceiling:
            local.append("AUTHORITY_WIDENING")

        qs = qualifications.get(candidate_id, [])
        if len(qs) != 1:
            local.append("QUALIFICATION_CARDINALITY")
        else:
            q = qs[0]
            if q.get("sbb_digest") != candidate.get("digest"):
                local.append("STALE_QUALIFICATION")
            if contract and q.get("contract") != contract.get("id"):
                local.append("CONTRACT_MISMATCH")
            if q.get("verdict") == "QUALIFIED" and candidate.get("digest") in (None, ""):
                local.append("UNKNOWN_PROMOTION")
            if q.get("verdict") == "QUALIFIED" and "AUTHORITY_WIDENING" in local:
                local.append("QUALIFICATION_AUTHORITY_LAUNDERING")

        receipt = {
            "schema": "ggen-marketplace.ea-qualification.v1",
            "candidate": candidate_id,
            "abb": candidate.get("abb"),
            "exact_subject": candidate.get("digest"),
            "contract": contract.get("id") if contract else None,
            "evidence": [q.get("id") for q in qs],
            "standing": "REFUSED" if local else "QUALIFIED",
            "refusal_codes": sorted(set(local)),
            "authority": "NONE",
        }
        receipt["qualification_digest"] = canonical_digest(receipt)
        receipts.append(receipt)
        refusals.extend({"code": code, "subject": candidate_id} for code in sorted(set(local)))

    body = {
        "schema": "ggen-marketplace.ea-court.v1",
        "graph_digest": canonical_digest(graph),
        "receipts": receipts,
        "refusals": refusals,
        "authority": "NONE",
    }
    body["court_digest"] = canonical_digest(body)
    return body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture")
    parser.add_argument("--expect-refusal")
    args = parser.parse_args()

    graph = json.loads(Path(args.fixture).read_text())
    first = qualify(graph)
    second = qualify(graph)

    if first != second:
        print("REFUSED[NON_DETERMINISTIC_COURT]")
        return 3

    print(json.dumps(first, sort_keys=True, separators=(",", ":")))

    codes = {item["code"] for item in first["refusals"]}
    if args.expect_refusal:
        if args.expect_refusal not in codes:
            print(f"REFUSED[MISSING_EXPECTED_FALSIFIER]: {args.expect_refusal}")
            return 4
        return 0

    if codes:
        print("REFUSED[" + ",".join(sorted(codes)) + "]")
        return 2

    print("ALIVE: exact-subject ABB/SBB qualification; authority NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
