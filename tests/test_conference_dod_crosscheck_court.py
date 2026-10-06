"""CG7 conference-commerce lane: the commerce DoD cross-check court.

The event's purchase evidence — AGNTCon exhibitor-floor customers (sponsor /
gold / booth tiers) provisioned through the real commerce sim (CG1 fixture) —
is fed to the REAL Fortune-5 commerce Definition-of-Done court
(`packs/chatman-marketplace-commerce-dod-pack/gates/definition_of_done.py`,
`classify()`). The court must:

1. classify each honest sim-mode evidence payload as PARTIAL_ALIVE — never
   ALIVE without `exact_provider` evidence;
2. refuse missing / dual billing authority
   (REFUSED_BILLING_AUTHORITY_CARDINALITY);
3. refuse evidence for a different subject
   (REFUSED_RECEIPT_SUBJECT_MISMATCH);
4. fire the entitlement_before_capability_grant failure-boundary blocker when
   a capability is granted without entitlement.

Honest framing: the sim is not a provider. Sim-mode standing is PARTIAL_ALIVE;
the court proves the DoD does not rubber-stamp it to ALIVE.

Chicago discipline: the real DoD court over real fixture-derived evidence.
No mocks.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(
    0, str(Path(__file__).resolve().parents[1]
           / "packs" / "chatman-marketplace-commerce-dod-pack" / "gates"))

from test_conference_commerce_fixture import fixture_singleton  # noqa: E402
from definition_of_done import classify, REQUIRED_CAPABILITIES  # noqa: E402

# Three event customers, one per conference tier. "booth" is a platinum-tier
# exhibitor booth on the fixture floor (the fixture's named tiers are
# sponsor/platinum/gold/small; booths are platinum exhibitors).
EVENT_CUSTOMERS = [
    ("akamai", "sponsor"),
    ("datadog", "gold"),
    ("temporal", "booth"),  # platinum on the floor; booth at the event
]

SHA40 = "a" * 40
DIGEST_A = "sha256:" + "b" * 64
DIGEST_B = "sha256:" + "c" * 64
AUTHORITY = "GOOGLE_CLOUD_MARKETPLACE"


# ---------------------------------------------------------------------------
# Evidence manufacture: sim purchase evidence -> DoD schema
# ---------------------------------------------------------------------------
def _receipt(rid: str, kind: str, subject_id: str, **extra) -> dict:
    r = {"id": rid, "kind": kind, "subject_id": subject_id,
         "parent_ids": []}
    r.update(extra)
    return r


def _base_payload(subject_id: str) -> dict:
    """A complete, honest sim-mode evidence payload for one event customer."""
    receipts = []
    phases = {}
    for phase in ("purchase", "entitlement", "provision", "usage", "billing",
                  "provider_acceptance", "lifecycle_transition",
                  "reconciliation"):
        rid = f"rcpt-{phase}"
        receipts.append(_receipt(rid, phase, subject_id))
        phases[phase] = {"complete": True, "receipt_id": rid}
    phases["lifecycle_transition"]["operations"] = [
        "renew", "expand", "reduce", "cancel"]

    boundaries = {}
    for i, name in enumerate((
            "provider_accept_before_local_persist",
            "entitlement_before_capability_grant",
            "meter_accept_before_receipt_persist",
            "monetary_adjustment_accept_before_receipt_persist",
            "cancellation_with_usage_in_flight",
            "private_offer_replacement",
            "concurrent_agreements",
            "duplicate_out_of_order_events",
            "late_rejected_metering")):
        rid = f"rcpt-boundary-{i}"
        receipts.append(_receipt(rid, "failure_boundary", subject_id))
        boundaries[name] = {"passed": True, "receipt_id": rid}

    receipts.append(_receipt(
        "rcpt-brce", "actuation", subject_id,
        intent_id="intent-conf-001", operation_id="op-conf-001",
        consequence_id="cons-conf-001", provider_effect_id="eff-conf-001",
        authority=AUTHORITY, persisted=True))
    receipts.append(_receipt(
        "rcpt-replay", "replay", subject_id,
        operation_id="op-conf-001", provider_effect_id="eff-conf-001"))

    return {
        "schema": "https://ggen.dev/marketplace/commerce-dod/v1",
        "subject": {
            "id": subject_id,
            "marketplace": "GCP_MARKETPLACE_SIM",
            "provider": "demo-provider",
            "marketplace_contract_id": "mkt-contract-001",
            "agreement_id": "agreement-conf-001",
            "environment": "conference-sim",
            "configuration_digest": DIGEST_A,
            "contract_digest": DIGEST_B,
            "source_sha": SHA40,
            "evidence_mode": "simulated",
        },
        "authority": {
            "active_billing_authorities": [AUTHORITY],
            "admitted_billing_authority": AUTHORITY,
        },
        "claim": {
            "required_capabilities": sorted(REQUIRED_CAPABILITIES),
        },
        "unsupported_capabilities": [],
        "execution": {
            "observed": True, "admitted": True, "executed": True,
            "verified": True, "consequence_observed": True,
            "exact_subject": True,
        },
        "receipts": receipts,
        "phases": phases,
        "brce": {
            "intent_id": "intent-conf-001",
            "operation_id": "op-conf-001",
            "consequence_id": "cons-conf-001",
            "provider_effect_id": "eff-conf-001",
            "receipt_id": "rcpt-brce",
            "do_path": "BRCE",
            "authority": AUTHORITY,
        },
        "replay": {
            "attempted": True, "verified": True,
            "operation_id": "op-conf-001",
            "provider_effect_id": "eff-conf-001",
            "receipt_id": "rcpt-replay",
            "additional_external_effects": 0,
        },
        "failure_boundaries": boundaries,
    }


@pytest.fixture(scope="module")
def evidence() -> dict[str, dict]:
    """DoD evidence payloads for three real fixture customers, keyed by tier.

    Grounds each payload in the CG1 fixture: the customer must exist on the
    real conference floor with an ACTIVE account and entitlement before its
    evidence payload is manufactured.
    """
    fx = fixture_singleton()
    fx.setup_customers()
    out: dict[str, dict] = {}
    for cid, tier in EVENT_CUSTOMERS:
        rec = fx.customers[cid]
        assert rec["tier"] in ("sponsor", "platinum", "gold")
        assert fx._get(f"/v1/billing/summary")["accounts"][cid][
            "state"] == "ACCOUNT_ACTIVE"
        payload = _base_payload(subject_id=cid)
        # bind the plan actually approved on the wire for this customer
        payload["subject"]["agreement_id"] = rec["entitlement"]["plan"]
        out[tier] = payload
    return out


# ---------------------------------------------------------------------------
# Court 1: honest sim-mode evidence classifies PARTIAL_ALIVE, never ALIVE
# ---------------------------------------------------------------------------
def test_sim_mode_evidence_is_partial_alive_never_alive(evidence) -> None:
    for tier, payload in evidence.items():
        result = classify(payload)
        assert result["standing"] == "PARTIAL_ALIVE", (tier, result)
        assert result["subject_id"] == dict(
            (t, c) for c, t in EVENT_CUSTOMERS)[tier]
        assert result["billing_authority"] == AUTHORITY
        # exactly one blocker: the missing exact-provider execution
        assert result["blockers"] == ["EXACT_PROVIDER_EXECUTION_REQUIRED"]
        assert result["refusals"] == []
        assert result["unsupported"] == []
        assert result["receipt_count"] == 19  # 8 phases + 9 boundaries + brce + replay


def test_exact_provider_mode_would_be_alive(evidence) -> None:
    """The only path to ALIVE is exact_provider evidence — the court's
    promotion gate is the evidence mode, not the payload's completeness."""
    payload = copy.deepcopy(evidence["sponsor"])
    payload["subject"]["evidence_mode"] = "exact_provider"
    result = classify(payload)
    assert result["standing"] == "ALIVE"
    assert result["blockers"] == []
    # a sim cannot produce this: flip it back and ALIVE disappears
    payload["subject"]["evidence_mode"] = "simulated"
    assert classify(payload)["standing"] == "PARTIAL_ALIVE"


# ---------------------------------------------------------------------------
# Court 2: billing authority cardinality — fail closed both directions
# ---------------------------------------------------------------------------
def test_missing_billing_authority_refused(evidence) -> None:
    payload = copy.deepcopy(evidence["sponsor"])
    payload["authority"]["active_billing_authorities"] = []
    result = classify(payload)
    assert "REFUSED_BILLING_AUTHORITY_CARDINALITY" in result["refusals"]
    assert result["standing"] == "BLOCKED"
    assert result["billing_authority"] is None


def test_dual_billing_authority_refused(evidence) -> None:
    payload = copy.deepcopy(evidence["sponsor"])
    payload["authority"]["active_billing_authorities"] = [
        AUTHORITY, "AWS_MARKETPLACE"]
    result = classify(payload)
    assert "REFUSED_BILLING_AUTHORITY_CARDINALITY" in result["refusals"]
    assert result["standing"] == "BLOCKED"


# ---------------------------------------------------------------------------
# Court 3: evidence for a different subject is refused
# ---------------------------------------------------------------------------
def test_foreign_subject_receipt_refused(evidence) -> None:
    payload = copy.deepcopy(evidence["sponsor"])
    # one receipt claims a different customer's subject_id
    payload["receipts"][0]["subject_id"] = "datadog"
    result = classify(payload)
    assert "REFUSED_RECEIPT_SUBJECT_MISMATCH" in result["refusals"]
    assert result["standing"] == "BLOCKED"


# ---------------------------------------------------------------------------
# Court 4: entitlement_before_capability_grant failure boundary fires
# ---------------------------------------------------------------------------
def test_entitlement_before_capability_boundary_fires(evidence) -> None:
    """Capability granted without entitlement: the boundary court must fire."""
    payload = copy.deepcopy(evidence["gold"])
    payload["failure_boundaries"]["entitlement_before_capability_grant"] = {
        "passed": False, "receipt_id": "rcpt-boundary-1"}
    result = classify(payload)
    assert ("FAILURE_BOUNDARY_ENTITLEMENT_BEFORE_CAPABILITY_GRANT_REQUIRED"
            in result["blockers"])
    assert result["standing"] == "BLOCKED"


def test_entitlement_before_capability_boundary_receipt_missing(evidence) -> None:
    payload = copy.deepcopy(evidence["gold"])
    payload["failure_boundaries"]["entitlement_before_capability_grant"] = {
        "passed": True, "receipt_id": "rcpt-does-not-exist"}
    result = classify(payload)
    assert "REFUSED_FAILURE_BOUNDARY_RECEIPT_MISSING" in result["refusals"]
    assert result["standing"] == "BLOCKED"


# ---------------------------------------------------------------------------
# Court 5: the court is not vacuous — removing purchase evidence blocks
# ---------------------------------------------------------------------------
def test_missing_purchase_phase_blocks(evidence) -> None:
    payload = copy.deepcopy(evidence["booth"])
    payload["phases"]["purchase"]["complete"] = False
    result = classify(payload)
    assert "PHASE_PURCHASE_INCOMPLETE" in result["blockers"]
    assert result["standing"] == "BLOCKED"


def test_non_brce_actuation_refused(evidence) -> None:
    payload = copy.deepcopy(evidence["booth"])
    payload["brce"]["do_path"] = "direct"
    result = classify(payload)
    assert "REFUSED_NON_BRCE_ACTUATION" in result["refusals"]
    assert result["standing"] == "BLOCKED"
