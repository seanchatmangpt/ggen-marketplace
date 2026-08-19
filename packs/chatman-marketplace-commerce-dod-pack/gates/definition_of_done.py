#!/usr/bin/env python3
"""Fail-closed marketplace-commerce Definition-of-Done verifier.

This verifier classifies supplied evidence; it never calls a marketplace and never
turns simulated evidence into provider standing. `ALIVE` is reserved for an
exact-provider evidence bundle that proves the admitted commercial subject,
BRCE-only actuation, provider consequence, durable receipt, replay identity,
required lifecycle phases, reconciliation, and crash-boundary behavior.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA = "https://ggen.dev/marketplace/commerce-dod/v1"
STANDINGS = frozenset({"UNKNOWN", "PARTIAL_ALIVE", "ALIVE", "BLOCKED", "BUILD_BROKEN", "UNSUPPORTED"})
EVIDENCE_MODES = frozenset({"static", "simulated", "exact_provider"})
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
REQUIRED_PHASES = (
    "purchase",
    "entitlement",
    "provision",
    "usage",
    "billing",
    "provider_acceptance",
    "lifecycle_transition",
    "reconciliation",
)
CORE_FAILURE_BOUNDARIES = (
    "provider_accept_before_local_persist",
    "entitlement_before_capability_grant",
    "meter_accept_before_receipt_persist",
    "duplicate_out_of_order_events",
)
KNOWN_UNSUPPORTED = frozenset(
    {
        "UNSUPPORTED_MARKETPLACE_PRICING_MODEL",
        "UNSUPPORTED_PRIVATE_OFFER_SEMANTICS",
        "UNSUPPORTED_METERING_GRANULARITY",
        "UNSUPPORTED_IDENTITY_BINDING",
        "UNSUPPORTED_CONTRACT_TRANSITION",
    }
)


@dataclass
class Verdict:
    blockers: list[str] = field(default_factory=list)
    refusals: list[str] = field(default_factory=list)
    unsupported: list[str] = field(default_factory=list)

    def block(self, code: str) -> None:
        if code not in self.blockers:
            self.blockers.append(code)

    def refuse(self, code: str) -> None:
        if code not in self.refusals:
            self.refusals.append(code)

    def unsupported_capability(self, code: str) -> None:
        if code not in self.unsupported:
            self.unsupported.append(code)


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _canonical_digest(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _receipt_index(payload: dict[str, Any], verdict: Verdict) -> dict[str, dict[str, Any]]:
    receipts = _list(payload.get("receipts"))
    index: dict[str, dict[str, Any]] = {}
    for raw in receipts:
        if not isinstance(raw, dict):
            verdict.refuse("REFUSED_RECEIPT_NOT_OBJECT")
            continue
        receipt_id = _text(raw.get("id"))
        if not receipt_id:
            verdict.refuse("REFUSED_RECEIPT_ID_MISSING")
            continue
        if receipt_id in index:
            verdict.refuse("REFUSED_DUPLICATE_RECEIPT_ID")
            continue
        index[receipt_id] = raw
    return index


def _verify_receipt_dag(index: dict[str, dict[str, Any]], verdict: Verdict) -> None:
    for receipt in index.values():
        parents = receipt.get("parent_ids", [])
        if not isinstance(parents, list) or not all(isinstance(item, str) and item for item in parents):
            verdict.refuse("REFUSED_RECEIPT_PARENTS_INVALID")
            continue
        for parent in parents:
            if parent not in index:
                verdict.refuse("REFUSED_RECEIPT_PARENT_MISSING")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            verdict.refuse("REFUSED_RECEIPT_DAG_CYCLE")
            return
        if node in visited:
            return
        visiting.add(node)
        for parent in _list(index[node].get("parent_ids")):
            if isinstance(parent, str) and parent in index:
                visit(parent)
        visiting.remove(node)
        visited.add(node)

    for receipt_id in index:
        visit(receipt_id)


def _verify_subject(payload: dict[str, Any], verdict: Verdict) -> tuple[dict[str, Any], str]:
    subject = _dict(payload.get("subject"))
    subject_id = _text(subject.get("id"))
    required_text = (
        "id",
        "marketplace",
        "provider",
        "marketplace_contract_id",
        "agreement_id",
        "environment",
        "configuration_digest",
        "contract_digest",
        "source_sha",
    )
    for key in required_text:
        if not _text(subject.get(key)):
            verdict.block(f"MISSING_SUBJECT_{key.upper()}")
    source_sha = _text(subject.get("source_sha"))
    if source_sha and not SHA40.fullmatch(source_sha):
        verdict.refuse("REFUSED_SOURCE_SHA_NOT_EXACT")
    for key in ("configuration_digest", "contract_digest"):
        value = _text(subject.get(key))
        if value and not SHA256.fullmatch(value):
            verdict.refuse(f"REFUSED_{key.upper()}_INVALID")
    mode = _text(subject.get("evidence_mode"))
    if mode not in EVIDENCE_MODES:
        verdict.refuse("REFUSED_EVIDENCE_MODE_INVALID")
    return subject, subject_id


def _verify_authority(payload: dict[str, Any], verdict: Verdict) -> str:
    authority = _dict(payload.get("authority"))
    raw = _list(authority.get("active_billing_authorities"))
    active = [item for item in raw if isinstance(item, str) and item]
    if len(active) != 1:
        verdict.refuse("REFUSED_BILLING_AUTHORITY_CARDINALITY")
        return ""
    admitted = _text(authority.get("admitted_billing_authority"))
    if admitted != active[0]:
        verdict.refuse("REFUSED_BILLING_AUTHORITY_MISMATCH")
    return active[0]


def _verify_required_capabilities(payload: dict[str, Any], verdict: Verdict) -> None:
    claim = _dict(payload.get("claim"))
    required_set = {item for item in _list(claim.get("required_capabilities")) if isinstance(item, str) and item}
    for raw in _list(payload.get("unsupported_capabilities")):
        if not isinstance(raw, dict):
            verdict.refuse("REFUSED_UNSUPPORTED_CAPABILITY_INVALID")
            continue
        capability = _text(raw.get("capability"))
        code = _text(raw.get("code"))
        if not capability or code not in KNOWN_UNSUPPORTED:
            verdict.refuse("REFUSED_UNSUPPORTED_CAPABILITY_INVALID")
            continue
        if capability in required_set:
            verdict.unsupported_capability(code)


def _verify_execution(payload: dict[str, Any], verdict: Verdict) -> None:
    execution = _dict(payload.get("execution"))
    for key in ("observed", "admitted", "executed", "verified", "consequence_observed", "exact_subject"):
        if execution.get(key) is not True:
            verdict.block(f"EXECUTION_{key.upper()}_REQUIRED")


def _verify_phases(payload: dict[str, Any], index: dict[str, dict[str, Any]], subject_id: str, verdict: Verdict) -> None:
    phases = _dict(payload.get("phases"))
    for phase in REQUIRED_PHASES:
        entry = _dict(phases.get(phase))
        receipt_id = _text(entry.get("receipt_id"))
        if entry.get("complete") is not True or not receipt_id:
            verdict.block(f"PHASE_{phase.upper()}_INCOMPLETE")
            continue
        receipt = index.get(receipt_id)
        if receipt is None:
            verdict.refuse("REFUSED_PHASE_RECEIPT_MISSING")
            continue
        if _text(receipt.get("subject_id")) != subject_id:
            verdict.refuse("REFUSED_RECEIPT_SUBJECT_MISMATCH")
        if _text(receipt.get("kind")) != phase:
            verdict.refuse("REFUSED_PHASE_RECEIPT_KIND_MISMATCH")


def _verify_brce(payload: dict[str, Any], index: dict[str, dict[str, Any]], subject_id: str, authority: str, verdict: Verdict) -> None:
    brce = _dict(payload.get("brce"))
    for key in ("intent_id", "operation_id", "consequence_id", "provider_effect_id", "receipt_id"):
        if not _text(brce.get(key)):
            verdict.block(f"BRCE_{key.upper()}_REQUIRED")
    if brce.get("do_path") != "BRCE":
        verdict.refuse("REFUSED_NON_BRCE_ACTUATION")
    if _text(brce.get("authority")) != authority:
        verdict.refuse("REFUSED_BRCE_AUTHORITY_MISMATCH")
    receipt_id = _text(brce.get("receipt_id"))
    receipt = index.get(receipt_id)
    if receipt_id and receipt is None:
        verdict.refuse("REFUSED_BRCE_RECEIPT_MISSING")
        return
    if receipt is None:
        return
    bindings = {
        "subject_id": subject_id,
        "authority": authority,
        "operation_id": _text(brce.get("operation_id")),
        "consequence_id": _text(brce.get("consequence_id")),
        "provider_effect_id": _text(brce.get("provider_effect_id")),
    }
    for key, expected in bindings.items():
        if _text(receipt.get(key)) != expected:
            verdict.refuse(f"REFUSED_BRCE_RECEIPT_{key.upper()}_MISMATCH")
    if receipt.get("persisted") is not True:
        verdict.block("BRCE_RECEIPT_NOT_PERSISTED")


def _verify_replay(payload: dict[str, Any], verdict: Verdict) -> None:
    brce = _dict(payload.get("brce"))
    replay = _dict(payload.get("replay"))
    if replay.get("attempted") is not True or replay.get("verified") is not True:
        verdict.block("REPLAY_VERIFICATION_REQUIRED")
    if _text(replay.get("operation_id")) != _text(brce.get("operation_id")):
        verdict.refuse("REFUSED_REPLAY_OPERATION_ID_MISMATCH")
    if _text(replay.get("provider_effect_id")) != _text(brce.get("provider_effect_id")):
        verdict.refuse("REFUSED_REPLAY_PROVIDER_EFFECT_MISMATCH")
    if replay.get("additional_external_effects") != 0:
        verdict.refuse("REFUSED_REPLAY_DUPLICATE_EXTERNAL_EFFECT")
    if not _text(replay.get("receipt_id")):
        verdict.block("REPLAY_RECEIPT_REQUIRED")


def _verify_failure_boundaries(payload: dict[str, Any], index: dict[str, dict[str, Any]], verdict: Verdict) -> None:
    boundaries = _dict(payload.get("failure_boundaries"))
    for name in CORE_FAILURE_BOUNDARIES:
        entry = _dict(boundaries.get(name))
        if entry.get("passed") is not True:
            verdict.block(f"FAILURE_BOUNDARY_{name.upper()}_REQUIRED")
            continue
        receipt_id = _text(entry.get("receipt_id"))
        if not receipt_id:
            verdict.block(f"FAILURE_BOUNDARY_{name.upper()}_RECEIPT_REQUIRED")
        elif receipt_id not in index:
            verdict.refuse("REFUSED_FAILURE_BOUNDARY_RECEIPT_MISSING")


def classify(payload: dict[str, Any]) -> dict[str, Any]:
    verdict = Verdict()
    if payload.get("schema") != SCHEMA:
        verdict.refuse("REFUSED_SCHEMA_MISMATCH")

    subject, subject_id = _verify_subject(payload, verdict)
    authority = _verify_authority(payload, verdict)
    _verify_required_capabilities(payload, verdict)
    _verify_execution(payload, verdict)
    index = _receipt_index(payload, verdict)
    _verify_receipt_dag(index, verdict)
    _verify_phases(payload, index, subject_id, verdict)
    _verify_brce(payload, index, subject_id, authority, verdict)
    _verify_replay(payload, verdict)
    _verify_failure_boundaries(payload, index, verdict)

    if verdict.refusals:
        standing = "BLOCKED"
    elif verdict.unsupported:
        standing = "UNSUPPORTED"
    elif verdict.blockers:
        standing = "BLOCKED"
    elif subject.get("evidence_mode") != "exact_provider":
        standing = "PARTIAL_ALIVE"
        verdict.block("EXACT_PROVIDER_EXECUTION_REQUIRED")
    else:
        standing = "ALIVE"

    assert standing in STANDINGS
    return {
        "schema": SCHEMA,
        "standing": standing,
        "subject_id": subject_id or None,
        "marketplace": subject.get("marketplace"),
        "provider": subject.get("provider"),
        "billing_authority": authority or None,
        "blockers": sorted(verdict.blockers),
        "refusals": sorted(verdict.refusals),
        "unsupported": sorted(verdict.unsupported),
        "receipt_count": len(index),
        "evidence_digest": _canonical_digest(payload),
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
    parser.add_argument("evidence", type=Path, help="normalized marketplace commerce evidence JSON")
    parser.add_argument(
        "--classify-only",
        action="store_true",
        help="return success for any parseable evidence while still emitting its standing; default is the Definition-of-Done gate",
    )
    args = parser.parse_args(argv)
    try:
        result = classify(load(args.evidence))
    except ValueError as exc:
        result = {
            "schema": SCHEMA,
            "standing": "BLOCKED",
            "blockers": [],
            "refusals": [str(exc)],
            "unsupported": [],
            "receipt_count": 0,
            "evidence_digest": None,
        }
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    if args.classify_only:
        return 0
    return 0 if result["standing"] == "ALIVE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
