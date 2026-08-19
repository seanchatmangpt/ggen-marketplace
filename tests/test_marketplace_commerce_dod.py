from __future__ import annotations

import importlib.util
import sys
from copy import deepcopy
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "packs/chatman-marketplace-commerce-dod-pack/gates/definition_of_done.py"
S = importlib.util.spec_from_file_location("marketplace_commerce_dod", P)
assert S is not None and S.loader is not None
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)
classify = M.classify

SUBJECT = "agreement:acme:aws:contract-42"
AUTHORITY = "AWS_MARKETPLACE"
CAPABILITIES = [
    "contract", "entitlement", "provisioning", "metering", "billing",
    "lifecycle", "reconciliation", "private_offer", "monetary_adjustment",
    "concurrent_agreements", "late_metering",
]
PHASES = [
    "purchase", "entitlement", "provision", "usage", "billing",
    "provider_acceptance", "lifecycle_transition", "reconciliation",
]
BOUNDARIES = {
    "provider_accept_before_local_persist": "provider",
    "entitlement_before_capability_grant": "entitlement",
    "meter_accept_before_receipt_persist": "meter",
    "monetary_adjustment_accept_before_receipt_persist": "adjustment",
    "cancellation_with_usage_in_flight": "cancel",
    "private_offer_replacement": "private-offer",
    "concurrent_agreements": "concurrent",
    "duplicate_out_of_order_events": "events",
    "late_rejected_metering": "late-metering",
}


def receipt(rid, kind, parents, **extra):
    value = {"id": rid, "kind": kind, "subject_id": SUBJECT, "parent_ids": parents}
    value.update(extra)
    return value


def evidence(mode="exact_provider"):
    receipts, parents = [], []
    for phase in PHASES:
        rid = f"r:{phase}"
        receipts.append(receipt(rid, phase, parents.copy()))
        parents = [rid]
    receipts += [
        receipt(
            "r:brce", "commercial_actuation", ["r:billing"],
            intent_id="intent:42", authority=AUTHORITY,
            operation_id="op:meter:2026-08-19T10",
            consequence_id="consequence:invoice-line-42",
            provider_effect_id="aws:meter-record:42", persisted=True,
        ),
        receipt(
            "r:replay", "replay", ["r:brce"],
            operation_id="op:meter:2026-08-19T10",
            provider_effect_id="aws:meter-record:42",
        ),
    ]
    receipts += [receipt(f"r:boundary-{suffix}", "failure_boundary", ["r:brce"]) for suffix in BOUNDARIES.values()]
    phases = {phase: {"complete": True, "receipt_id": f"r:{phase}"} for phase in PHASES}
    phases["lifecycle_transition"]["operations"] = ["renew", "expand", "reduce", "cancel"]
    return {
        "schema": "https://ggen.dev/marketplace/commerce-dod/v1",
        "subject": {
            "id": SUBJECT, "marketplace": "aws", "provider": "aws-marketplace",
            "marketplace_contract_id": "contract-42", "agreement_id": "agreement-42",
            "environment": "aws-marketplace-test", "evidence_mode": mode,
            "source_sha": "a" * 40, "configuration_digest": "sha256:" + "b" * 64,
            "contract_digest": "sha256:" + "c" * 64,
        },
        "claim": {"required_capabilities": CAPABILITIES.copy()},
        "unsupported_capabilities": [],
        "authority": {"active_billing_authorities": [AUTHORITY], "admitted_billing_authority": AUTHORITY},
        "execution": {"observed": True, "admitted": True, "executed": True, "verified": True,
                      "consequence_observed": True, "exact_subject": True},
        "phases": phases,
        "brce": {"do_path": "BRCE", "intent_id": "intent:42", "operation_id": "op:meter:2026-08-19T10",
                 "authority": AUTHORITY, "consequence_id": "consequence:invoice-line-42",
                 "provider_effect_id": "aws:meter-record:42", "receipt_id": "r:brce"},
        "replay": {"attempted": True, "verified": True, "operation_id": "op:meter:2026-08-19T10",
                   "provider_effect_id": "aws:meter-record:42", "additional_external_effects": 0,
                   "receipt_id": "r:replay"},
        "failure_boundaries": {name: {"passed": True, "receipt_id": f"r:boundary-{suffix}"}
                               for name, suffix in BOUNDARIES.items()},
        "receipts": receipts,
    }


def blocked(mutator, code, bucket="refusals"):
    value = evidence(); mutator(value); result = classify(value)
    assert result["standing"] == "BLOCKED"
    assert code in result[bucket]


def test_exact_provider_complete_evidence_reaches_alive():
    assert classify(evidence())["standing"] == "ALIVE"


def test_simulation_cannot_crown_alive():
    result = classify(evidence("simulated"))
    assert result["standing"] == "PARTIAL_ALIVE"
    assert "EXACT_PROVIDER_EXECUTION_REQUIRED" in result["blockers"]


def test_dual_billing_authority_refused():
    blocked(lambda e: e["authority"]["active_billing_authorities"].append("DIRECT_STRIPE"),
            "REFUSED_BILLING_AUTHORITY_CARDINALITY")


def test_malformed_billing_authority_refused():
    blocked(lambda e: e["authority"]["active_billing_authorities"].append({"authority": "DIRECT_STRIPE"}),
            "REFUSED_BILLING_AUTHORITY_LIST_INVALID")


def test_non_brce_do_refused():
    blocked(lambda e: e["brce"].update(do_path="DIRECT_PROVIDER_CALL"), "REFUSED_NON_BRCE_ACTUATION")


def test_replay_effect_must_match():
    blocked(lambda e: e["replay"].update(provider_effect_id="duplicate"), "REFUSED_REPLAY_PROVIDER_EFFECT_MISMATCH")


def test_replay_cannot_duplicate_external_effect():
    blocked(lambda e: e["replay"].update(additional_external_effects=1), "REFUSED_REPLAY_DUPLICATE_EXTERNAL_EFFECT")


def test_replay_receipt_must_exist():
    blocked(lambda e: e["replay"].update(receipt_id="r:missing"), "REFUSED_REPLAY_RECEIPT_MISSING")


def test_phase_receipt_binds_exact_subject():
    def mutate(e):
        next(x for x in e["receipts"] if x["id"] == "r:provider_acceptance")["subject_id"] = "other"
    blocked(mutate, "REFUSED_RECEIPT_SUBJECT_MISMATCH")


def test_brce_receipt_binds_intent_operation_and_effect():
    def mutate(e):
        next(x for x in e["receipts"] if x["id"] == "r:brce")["intent_id"] = "intent:other"
    blocked(mutate, "REFUSED_BRCE_RECEIPT_INTENT_ID_MISMATCH")


def test_receipt_graph_is_acyclic():
    def mutate(e):
        next(x for x in e["receipts"] if x["id"] == "r:purchase")["parent_ids"] = ["r:reconciliation"]
    blocked(mutate, "REFUSED_RECEIPT_DAG_CYCLE")


def test_all_fortune5_capabilities_are_required():
    def mutate(e): e["claim"]["required_capabilities"].remove("concurrent_agreements")
    blocked(mutate, "REQUIRED_CAPABILITY_CONCURRENT_AGREEMENTS_MISSING", "blockers")


def test_unsupported_required_capability_is_not_alive():
    value = evidence()
    value["unsupported_capabilities"] = [{"capability": "private_offer", "code": "UNSUPPORTED_PRIVATE_OFFER_SEMANTICS"}]
    result = classify(value)
    assert result["standing"] == "UNSUPPORTED"


def test_all_nine_failure_boundaries_are_required():
    def mutate(e): del e["failure_boundaries"]["provider_accept_before_local_persist"]
    blocked(mutate, "FAILURE_BOUNDARY_PROVIDER_ACCEPT_BEFORE_LOCAL_PERSIST_REQUIRED", "blockers")


def test_boundary_receipt_must_be_boundary_evidence():
    def mutate(e): e["failure_boundaries"]["concurrent_agreements"]["receipt_id"] = "r:usage"
    blocked(mutate, "REFUSED_FAILURE_BOUNDARY_RECEIPT_KIND_MISMATCH")


def test_full_lifecycle_operations_required():
    def mutate(e): e["phases"]["lifecycle_transition"]["operations"].remove("cancel")
    blocked(mutate, "LIFECYCLE_RENEW_EXPAND_REDUCE_CANCEL_REQUIRED", "blockers")


def test_reconciliation_phase_required():
    def mutate(e): e["phases"]["reconciliation"]["complete"] = False
    blocked(mutate, "PHASE_RECONCILIATION_INCOMPLETE", "blockers")


def test_digest_is_deterministic():
    assert classify(evidence())["evidence_digest"] == classify(deepcopy(evidence()))["evidence_digest"]
