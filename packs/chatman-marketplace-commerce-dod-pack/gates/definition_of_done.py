#!/usr/bin/env python3
"""Fail-closed Fortune-5 marketplace-commerce Definition-of-Done court.

The court classifies normalized evidence only. It never calls a provider and it
never promotes static or simulated evidence to provider standing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA = "https://ggen.dev/marketplace/commerce-dod/v1"
EVIDENCE_MODES = {"static", "simulated", "exact_provider"}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
REQUIRED_PHASES = (
    "purchase", "entitlement", "provision", "usage", "billing",
    "provider_acceptance", "lifecycle_transition", "reconciliation",
)
REQUIRED_CAPABILITIES = {
    "contract", "entitlement", "provisioning", "metering", "billing",
    "lifecycle", "reconciliation", "private_offer", "monetary_adjustment",
    "concurrent_agreements", "late_metering",
}
REQUIRED_LIFECYCLE_OPERATIONS = {"renew", "expand", "reduce", "cancel"}
REQUIRED_FAILURE_BOUNDARIES = (
    "provider_accept_before_local_persist",
    "entitlement_before_capability_grant",
    "meter_accept_before_receipt_persist",
    "monetary_adjustment_accept_before_receipt_persist",
    "cancellation_with_usage_in_flight",
    "private_offer_replacement",
    "concurrent_agreements",
    "duplicate_out_of_order_events",
    "late_rejected_metering",
)
KNOWN_AUTHORITIES = {
    "AWS_MARKETPLACE", "MICROSOFT_MARKETPLACE", "GOOGLE_CLOUD_MARKETPLACE",
    "ORACLE_MARKETPLACE", "IBM_MARKETPLACE", "SAP_MARKETPLACE",
    "SALESFORCE_APPEXCHANGE", "DIRECT_STRIPE", "GENERIC_MARKETPLACE",
}
KNOWN_UNSUPPORTED = {
    "UNSUPPORTED_MARKETPLACE_PRICING_MODEL",
    "UNSUPPORTED_PRIVATE_OFFER_SEMANTICS",
    "UNSUPPORTED_METERING_GRANULARITY",
    "UNSUPPORTED_IDENTITY_BINDING",
    "UNSUPPORTED_CONTRACT_TRANSITION",
}


def obj(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def seq(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def add(items: list[str], code: str) -> None:
    if code not in items:
        items.append(code)


def evidence_digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def receipt_index(payload: dict[str, Any], refusals: list[str]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for raw in seq(payload.get("receipts")):
        if not isinstance(raw, dict):
            add(refusals, "REFUSED_RECEIPT_NOT_OBJECT")
            continue
        rid = text(raw.get("id"))
        if not rid:
            add(refusals, "REFUSED_RECEIPT_ID_MISSING")
        elif rid in index:
            add(refusals, "REFUSED_DUPLICATE_RECEIPT_ID")
        else:
            index[rid] = raw
    return index


def verify_dag(index: dict[str, dict[str, Any]], refusals: list[str]) -> None:
    for receipt in index.values():
        parents = receipt.get("parent_ids", [])
        if not isinstance(parents, list) or not all(isinstance(x, str) and x for x in parents):
            add(refusals, "REFUSED_RECEIPT_PARENTS_INVALID")
            continue
        if any(parent not in index for parent in parents):
            add(refusals, "REFUSED_RECEIPT_PARENT_MISSING")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(rid: str) -> None:
        if rid in visiting:
            add(refusals, "REFUSED_RECEIPT_DAG_CYCLE")
            return
        if rid in visited:
            return
        visiting.add(rid)
        for parent in seq(index[rid].get("parent_ids")):
            if isinstance(parent, str) and parent in index:
                visit(parent)
        visiting.remove(rid)
        visited.add(rid)

    for rid in index:
        visit(rid)


def classify(payload: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    refusals: list[str] = []
    unsupported: list[str] = []
    if payload.get("schema") != SCHEMA:
        add(refusals, "REFUSED_SCHEMA_MISMATCH")

    subject = obj(payload.get("subject"))
    subject_id = text(subject.get("id"))
    for key in (
        "id", "marketplace", "provider", "marketplace_contract_id", "agreement_id",
        "environment", "configuration_digest", "contract_digest", "source_sha",
    ):
        if not text(subject.get(key)):
            add(blockers, f"MISSING_SUBJECT_{key.upper()}")
    if text(subject.get("source_sha")) and not SHA40.fullmatch(text(subject.get("source_sha"))):
        add(refusals, "REFUSED_SOURCE_SHA_NOT_EXACT")
    for key in ("configuration_digest", "contract_digest"):
        value = text(subject.get(key))
        if value and not SHA256.fullmatch(value):
            add(refusals, f"REFUSED_{key.upper()}_INVALID")
    mode = text(subject.get("evidence_mode"))
    if mode not in EVIDENCE_MODES:
        add(refusals, "REFUSED_EVIDENCE_MODE_INVALID")

    authority = obj(payload.get("authority"))
    raw_authorities = seq(authority.get("active_billing_authorities"))
    if not all(isinstance(x, str) and x for x in raw_authorities):
        add(refusals, "REFUSED_BILLING_AUTHORITY_LIST_INVALID")
    active = [x for x in raw_authorities if isinstance(x, str) and x]
    admitted_authority = text(authority.get("admitted_billing_authority"))
    if len(active) != 1:
        add(refusals, "REFUSED_BILLING_AUTHORITY_CARDINALITY")
        billing_authority = ""
    else:
        billing_authority = active[0]
        if billing_authority not in KNOWN_AUTHORITIES:
            add(refusals, "REFUSED_BILLING_AUTHORITY_UNKNOWN")
        if admitted_authority != billing_authority:
            add(refusals, "REFUSED_BILLING_AUTHORITY_MISMATCH")

    claim = obj(payload.get("claim"))
    required_raw = seq(claim.get("required_capabilities"))
    if not all(isinstance(x, str) and x for x in required_raw):
        add(refusals, "REFUSED_REQUIRED_CAPABILITIES_INVALID")
    required = {x for x in required_raw if isinstance(x, str) and x}
    for capability in sorted(REQUIRED_CAPABILITIES - required):
        add(blockers, f"REQUIRED_CAPABILITY_{capability.upper()}_MISSING")
    for item in seq(payload.get("unsupported_capabilities")):
        if not isinstance(item, dict):
            add(refusals, "REFUSED_UNSUPPORTED_CAPABILITY_INVALID")
            continue
        capability, code = text(item.get("capability")), text(item.get("code"))
        if not capability or code not in KNOWN_UNSUPPORTED:
            add(refusals, "REFUSED_UNSUPPORTED_CAPABILITY_INVALID")
        elif capability in required:
            add(unsupported, code)

    execution = obj(payload.get("execution"))
    for key in ("observed", "admitted", "executed", "verified", "consequence_observed", "exact_subject"):
        if execution.get(key) is not True:
            add(blockers, f"EXECUTION_{key.upper()}_REQUIRED")

    receipts = receipt_index(payload, refusals)
    verify_dag(receipts, refusals)
    phases = obj(payload.get("phases"))
    for phase in REQUIRED_PHASES:
        entry = obj(phases.get(phase))
        rid = text(entry.get("receipt_id"))
        if entry.get("complete") is not True or not rid:
            add(blockers, f"PHASE_{phase.upper()}_INCOMPLETE")
            continue
        receipt = receipts.get(rid)
        if receipt is None:
            add(refusals, "REFUSED_PHASE_RECEIPT_MISSING")
            continue
        if text(receipt.get("subject_id")) != subject_id:
            add(refusals, "REFUSED_RECEIPT_SUBJECT_MISMATCH")
        if text(receipt.get("kind")) != phase:
            add(refusals, "REFUSED_PHASE_RECEIPT_KIND_MISMATCH")
        if phase == "lifecycle_transition":
            operations = entry.get("operations", [])
            if not isinstance(operations, list) or not all(isinstance(x, str) for x in operations):
                add(refusals, "REFUSED_LIFECYCLE_OPERATIONS_INVALID")
            elif not REQUIRED_LIFECYCLE_OPERATIONS.issubset(set(operations)):
                add(blockers, "LIFECYCLE_RENEW_EXPAND_REDUCE_CANCEL_REQUIRED")

    brce = obj(payload.get("brce"))
    for key in ("intent_id", "operation_id", "consequence_id", "provider_effect_id", "receipt_id"):
        if not text(brce.get(key)):
            add(blockers, f"BRCE_{key.upper()}_REQUIRED")
    if brce.get("do_path") != "BRCE":
        add(refusals, "REFUSED_NON_BRCE_ACTUATION")
    if text(brce.get("authority")) != billing_authority:
        add(refusals, "REFUSED_BRCE_AUTHORITY_MISMATCH")
    brce_receipt = receipts.get(text(brce.get("receipt_id")))
    if brce_receipt is None:
        add(refusals, "REFUSED_BRCE_RECEIPT_MISSING")
    else:
        for key, expected in {
            "subject_id": subject_id,
            "intent_id": text(brce.get("intent_id")),
            "authority": billing_authority,
            "operation_id": text(brce.get("operation_id")),
            "consequence_id": text(brce.get("consequence_id")),
            "provider_effect_id": text(brce.get("provider_effect_id")),
        }.items():
            if text(brce_receipt.get(key)) != expected:
                add(refusals, f"REFUSED_BRCE_RECEIPT_{key.upper()}_MISMATCH")
        if brce_receipt.get("persisted") is not True:
            add(blockers, "BRCE_RECEIPT_NOT_PERSISTED")

    replay = obj(payload.get("replay"))
    if replay.get("attempted") is not True or replay.get("verified") is not True:
        add(blockers, "REPLAY_VERIFICATION_REQUIRED")
    if text(replay.get("operation_id")) != text(brce.get("operation_id")):
        add(refusals, "REFUSED_REPLAY_OPERATION_ID_MISMATCH")
    if text(replay.get("provider_effect_id")) != text(brce.get("provider_effect_id")):
        add(refusals, "REFUSED_REPLAY_PROVIDER_EFFECT_MISMATCH")
    if replay.get("additional_external_effects") != 0:
        add(refusals, "REFUSED_REPLAY_DUPLICATE_EXTERNAL_EFFECT")
    replay_receipt = receipts.get(text(replay.get("receipt_id")))
    if replay_receipt is None:
        add(refusals, "REFUSED_REPLAY_RECEIPT_MISSING")
    else:
        if text(replay_receipt.get("kind")) != "replay":
            add(refusals, "REFUSED_REPLAY_RECEIPT_KIND_MISMATCH")
        if text(replay_receipt.get("subject_id")) != subject_id:
            add(refusals, "REFUSED_REPLAY_RECEIPT_SUBJECT_MISMATCH")
        if text(replay_receipt.get("operation_id")) != text(brce.get("operation_id")):
            add(refusals, "REFUSED_REPLAY_RECEIPT_OPERATION_ID_MISMATCH")
        if text(replay_receipt.get("provider_effect_id")) != text(brce.get("provider_effect_id")):
            add(refusals, "REFUSED_REPLAY_RECEIPT_PROVIDER_EFFECT_MISMATCH")

    boundaries = obj(payload.get("failure_boundaries"))
    for name in REQUIRED_FAILURE_BOUNDARIES:
        entry = obj(boundaries.get(name))
        rid = text(entry.get("receipt_id"))
        if entry.get("passed") is not True:
            add(blockers, f"FAILURE_BOUNDARY_{name.upper()}_REQUIRED")
            continue
        receipt = receipts.get(rid)
        if not rid:
            add(blockers, f"FAILURE_BOUNDARY_{name.upper()}_RECEIPT_REQUIRED")
        elif receipt is None:
            add(refusals, "REFUSED_FAILURE_BOUNDARY_RECEIPT_MISSING")
        else:
            if text(receipt.get("kind")) != "failure_boundary":
                add(refusals, "REFUSED_FAILURE_BOUNDARY_RECEIPT_KIND_MISMATCH")
            if text(receipt.get("subject_id")) != subject_id:
                add(refusals, "REFUSED_FAILURE_BOUNDARY_RECEIPT_SUBJECT_MISMATCH")

    if refusals:
        standing = "BLOCKED"
    elif unsupported:
        standing = "UNSUPPORTED"
    elif blockers:
        standing = "BLOCKED"
    elif mode != "exact_provider":
        standing = "PARTIAL_ALIVE"
        add(blockers, "EXACT_PROVIDER_EXECUTION_REQUIRED")
    else:
        standing = "ALIVE"
    return {
        "schema": SCHEMA,
        "standing": standing,
        "subject_id": subject_id or None,
        "marketplace": subject.get("marketplace"),
        "provider": subject.get("provider"),
        "billing_authority": billing_authority or None,
        "blockers": sorted(blockers),
        "refusals": sorted(refusals),
        "unsupported": sorted(unsupported),
        "receipt_count": len(receipts),
        "evidence_digest": evidence_digest(payload),
    }


def load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"REFUSED_EVIDENCE_UNREADABLE:{exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("REFUSED_EVIDENCE_ROOT_NOT_OBJECT")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--classify-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = classify(load(args.evidence))
    except ValueError as exc:
        result = {"schema": SCHEMA, "standing": "BLOCKED", "blockers": [],
                  "refusals": [str(exc)], "unsupported": [], "receipt_count": 0,
                  "evidence_digest": None}
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if args.classify_only or result["standing"] == "ALIVE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
