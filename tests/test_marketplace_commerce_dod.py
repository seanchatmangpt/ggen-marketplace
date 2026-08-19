from __future__ import annotations

import importlib.util
import sys
from copy import deepcopy
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "packs"
    / "chatman-marketplace-commerce-dod-pack"
    / "gates"
    / "definition_of_done.py"
)
spec = importlib.util.spec_from_file_location("marketplace_commerce_dod", MODULE_PATH)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
classify = module.classify

SUBJECT = "agreement:acme:aws:contract-42"
AUTHORITY = "AWS_MARKETPLACE"


def receipt(receipt_id: str, kind: str, parents: list[str], **extra):
    value = {
        "id": receipt_id,
        "kind": kind,
        "subject_id": SUBJECT,
        "parent_ids": parents,
    }
    value.update(extra)
    return value


def alive_evidence(mode: str = "exact_provider"):
    phases = [
        "purchase",
        "entitlement",
        "provision",
        "usage",
        "billing",
        "provider_acceptance",
        "lifecycle_transition",
        "reconciliation",
    ]
    receipts = []
    previous = []
    for phase in phases:
        receipt_id = f"r:{phase}"
        receipts.append(receipt(receipt_id, phase, previous.copy()))
        previous = [receipt_id]

    brce_receipt = {
        "id": "r:brce",
        "kind": "commercial_actuation",
        "subject_id": SUBJECT,
        "authority": AUTHORITY,
        "operation_id": "op:meter:2026-08-19T10",
        "consequence_id": "consequence:invoice-line-42",
        "provider_effect_id": "aws:meter-record:42",
        "persisted": True,
        "parent_ids": ["r:billing"],
    }
    replay_receipt = receipt("r:replay", "replay", ["r:brce"])
    boundary_receipts = [
        receipt("r:boundary-provider", "failure_boundary", ["r:brce"]),
        receipt("r:boundary-entitlement", "failure_boundary", ["r:entitlement"]),
        receipt("r:boundary-meter", "failure_boundary", ["r:brce"]),
        receipt("r:boundary-events", "failure_boundary", ["r:lifecycle_transition"]),
    ]
    receipts.extend([brce_receipt, replay_receipt, *boundary_receipts])

    return {
        "schema": "https://ggen.dev/marketplace/commerce-dod/v1",
        "subject": {
            "id": SUBJECT,
            "marketplace": "aws",
            "provider": "aws-marketplace",
            "marketplace_contract_id": "contract-42",
            "agreement_id": "agreement-42",
            "environment": "aws-marketplace-test",
            "evidence_mode": mode,
            "source_sha": "a" * 40,
            "configuration_digest": "sha256:" + "b" * 64,
            "contract_digest": "sha256:" + "c" * 64,
        },
        "claim": {"required_capabilities": ["contract", "metering", "lifecycle"]},
        "unsupported_capabilities": [],
        "authority": {
            "active_billing_authorities": [AUTHORITY],
            "admitted_billing_authority": AUTHORITY,
        },
        "execution": {
            "observed": True,
            "admitted": True,
            "executed": True,
            "verified": True,
            "consequence_observed": True,
            "exact_subject": True,
        },
        "phases": {phase: {"complete": True, "receipt_id": f"r:{phase}"} for phase in phases},
        "brce": {
            "do_path": "BRCE",
            "intent_id": "intent:42",
            "operation_id": "op:meter:2026-08-19T10",
            "authority": AUTHORITY,
            "consequence_id": "consequence:invoice-line-42",
            "provider_effect_id": "aws:meter-record:42",
            "receipt_id": "r:brce",
        },
        "replay": {
            "attempted": True,
            "verified": True,
            "operation_id": "op:meter:2026-08-19T10",
            "provider_effect_id": "aws:meter-record:42",
            "additional_external_effects": 0,
            "receipt_id": "r:replay",
        },
        "failure_boundaries": {
            "provider_accept_before_local_persist": {"passed": True, "receipt_id": "r:boundary-provider"},
            "entitlement_before_capability_grant": {"passed": True, "receipt_id": "r:boundary-entitlement"},
            "meter_accept_before_receipt_persist": {"passed": True, "receipt_id": "r:boundary-meter"},
            "duplicate_out_of_order_events": {"passed": True, "receipt_id": "r:boundary-events"},
        },
        "receipts": receipts,
    }


def test_exact_provider_complete_evidence_reaches_alive():
    result = classify(alive_evidence())
    assert result["standing"] == "ALIVE"
    assert result["refusals"] == []
    assert result["blockers"] == []


def test_simulation_cannot_crown_alive():
    result = classify(alive_evidence("simulated"))
    assert result["standing"] == "PARTIAL_ALIVE"
    assert "EXACT_PROVIDER_EXECUTION_REQUIRED" in result["blockers"]


def test_dual_billing_authority_is_typed_refusal():
    evidence = alive_evidence()
    evidence["authority"]["active_billing_authorities"].append("DIRECT_STRIPE")
    result = classify(evidence)
    assert result["standing"] == "BLOCKED"
    assert "REFUSED_BILLING_AUTHORITY_CARDINALITY" in result["refusals"]


def test_replay_must_bind_same_provider_effect():
    evidence = alive_evidence()
    evidence["replay"]["provider_effect_id"] = "aws:meter-record:duplicate"
    result = classify(evidence)
    assert result["standing"] == "BLOCKED"
    assert "REFUSED_REPLAY_PROVIDER_EFFECT_MISMATCH" in result["refusals"]


def test_replay_cannot_create_additional_external_effect():
    evidence = alive_evidence()
    evidence["replay"]["additional_external_effects"] = 1
    result = classify(evidence)
    assert result["standing"] == "BLOCKED"
    assert "REFUSED_REPLAY_DUPLICATE_EXTERNAL_EFFECT" in result["refusals"]


def test_missing_crash_boundary_proof_blocks_definition_of_done():
    evidence = alive_evidence()
    del evidence["failure_boundaries"]["provider_accept_before_local_persist"]
    result = classify(evidence)
    assert result["standing"] == "BLOCKED"
    assert "FAILURE_BOUNDARY_PROVIDER_ACCEPT_BEFORE_LOCAL_PERSIST_REQUIRED" in result["blockers"]


def test_phase_receipts_bind_exact_subject():
    evidence = alive_evidence()
    for item in evidence["receipts"]:
        if item["id"] == "r:provider_acceptance":
            item["subject_id"] = "agreement:other"
            break
    result = classify(evidence)
    assert result["standing"] == "BLOCKED"
    assert "REFUSED_RECEIPT_SUBJECT_MISMATCH" in result["refusals"]


def test_non_brce_financial_actuation_is_refused():
    evidence = alive_evidence()
    evidence["brce"]["do_path"] = "DIRECT_PROVIDER_CALL"
    result = classify(evidence)
    assert result["standing"] == "BLOCKED"
    assert "REFUSED_NON_BRCE_ACTUATION" in result["refusals"]


def test_required_unsupported_capability_is_unsupported_not_alive():
    evidence = alive_evidence()
    evidence["claim"]["required_capabilities"].append("private_offer")
    evidence["unsupported_capabilities"] = [
        {
            "capability": "private_offer",
            "code": "UNSUPPORTED_PRIVATE_OFFER_SEMANTICS",
        }
    ]
    result = classify(evidence)
    assert result["standing"] == "UNSUPPORTED"
    assert result["unsupported"] == ["UNSUPPORTED_PRIVATE_OFFER_SEMANTICS"]


def test_receipt_graph_must_be_acyclic():
    evidence = alive_evidence()
    evidence["receipts"][0]["parent_ids"] = ["r:reconciliation"]
    result = classify(evidence)
    assert result["standing"] == "BLOCKED"
    assert "REFUSED_RECEIPT_DAG_CYCLE" in result["refusals"]


def test_brce_receipt_must_bind_operation_and_provider_effect():
    evidence = alive_evidence()
    for item in evidence["receipts"]:
        if item["id"] == "r:brce":
            item["operation_id"] = "op:other"
            break
    result = classify(evidence)
    assert result["standing"] == "BLOCKED"
    assert "REFUSED_BRCE_RECEIPT_OPERATION_ID_MISMATCH" in result["refusals"]


def test_missing_required_lifecycle_phase_blocks_alive():
    evidence = alive_evidence()
    evidence["phases"]["reconciliation"]["complete"] = False
    result = classify(evidence)
    assert result["standing"] == "BLOCKED"
    assert "PHASE_RECONCILIATION_INCOMPLETE" in result["blockers"]


def test_evidence_digest_is_deterministic():
    first = classify(alive_evidence())
    second = classify(deepcopy(alive_evidence()))
    assert first["evidence_digest"] == second["evidence_digest"]
