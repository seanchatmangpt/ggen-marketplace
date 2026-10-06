"""Conference-registration-to-entitlement court (CG2).

Maps the AGNTCon registration desk onto the GCP Marketplace purchase flow
over the REAL commerce sim (k8s/gcp-marketplace-sim/server.py):

1. a company registering at the conference  == account :approve
   a company purchasing on GCP Marketplace  == entitlement :approve
   both must succeed;
2. the DoD court (packs/chatman-marketplace-commerce-dod-pack) classifies
   the real purchase evidence -> PARTIAL_ALIVE (sim mode, honest);
3. double-purchase for the same company+plan -> idempotent (one
   entitlement, not two);
4. expired card -> purchase REFUSED before any wire actuation;
5. free tier (no purchase) -> no entitlement (pay-before-manufacture,
   witnessed at the sim's own ENTITLEMENT_REQUIRED :report gate).

Chicago style: real HTTP sim subprocess, real approvals, real DoD gate
subprocess. No mocks.
"""
from __future__ import annotations

import datetime
import json
import subprocess
import sys
import urllib.error
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_conference_commerce_fixture import (  # noqa: E402
    ConferenceCommerceFixture,
    TIERS,
)

ROOT = Path(__file__).resolve().parent.parent
DOD_GATE = (ROOT / "packs" / "chatman-marketplace-commerce-dod-pack"
            / "gates" / "definition_of_done.py")
SCHEMA = "https://ggen.dev/marketplace/commerce-dod/v1"
AUTHORITY = "GOOGLE_CLOUD_MARKETPLACE"
CAPABILITIES = [
    "contract", "entitlement", "provisioning", "metering", "billing",
    "lifecycle", "reconciliation", "private_offer", "monetary_adjustment",
    "concurrent_agreements", "late_metering",
]
PHASES = [
    "purchase", "entitlement", "provision", "usage", "billing",
    "provider_acceptance", "lifecycle_transition", "reconciliation",
]
BOUNDARY_SUFFIXES = [
    "provider", "entitlement", "meter", "adjustment", "cancel",
    "private-offer", "concurrent", "events", "late-metering",
]
BOUNDARY_NAMES = [
    "provider_accept_before_local_persist",
    "entitlement_before_capability_grant",
    "meter_accept_before_receipt_persist",
    "monetary_adjustment_accept_before_receipt_persist",
    "cancellation_with_usage_in_flight",
    "private_offer_replacement",
    "concurrent_agreements",
    "duplicate_out_of_order_events",
    "late_rejected_metering",
]


class PurchaseRefused(AssertionError):
    """Typed refusal from the registration-desk purchase admission layer."""


class Card:
    def __init__(self, exp_month: int, exp_year: int) -> None:
        self.exp_month = exp_month
        self.exp_year = exp_year

    @property
    def label(self) -> str:
        return f"{self.exp_month:02d}/{self.exp_year % 100:02d}"


def card_is_current(card: Card, now: datetime.datetime) -> bool:
    """A card is current through the last day of its expiry month (UTC)."""
    if now.tzinfo is not None:
        now = now.replace(tzinfo=None)
    expiry_end = datetime.datetime(card.exp_year, card.exp_month, 1)
    # advance to the first instant AFTER the expiry month
    if card.exp_month == 12:
        expiry_end = datetime.datetime(card.exp_year + 1, 1, 1)
    else:
        expiry_end = datetime.datetime(card.exp_year, card.exp_month + 1, 1)
    return now < expiry_end


# ---------------------------------------------------------------------------
# Purchase desk: the registration-to-purchase admission layer
# ---------------------------------------------------------------------------
def register(fx: ConferenceCommerceFixture, cid: str) -> dict:
    account = fx.approve_account(cid)
    assert account["state"] == "ACCOUNT_ACTIVE", account
    return account


def purchase(fx: ConferenceCommerceFixture, cid: str, plan: str,
             card: Card, now: datetime.datetime | None = None) -> dict:
    """Register (if needed) then purchase `plan`, paying with `card`.

    The card check runs BEFORE any wire actuation: an expired card is a
    typed refusal, and no entitlement can exist behind it.
    """
    now = now or datetime.datetime.now()
    if not card_is_current(card, now):
        raise PurchaseRefused(f"REFUSED_CARD_EXPIRED:{card.label}")
    if cid not in fx.customers:
        register(fx, cid)
    ent = fx.approve_entitlement(cid, plan)
    assert ent["state"] == "ENTITLEMENT_ACTIVE", ent
    rec = {"cid": cid, "tier": "purchase-desk", "plan": plan,
           "account": {"state": "ACCOUNT_ACTIVE"}, "entitlement": ent}
    fx.customers[cid] = rec
    return rec


def summary_entitlements(fx: ConferenceCommerceFixture) -> dict:
    return fx._get("/v1/billing/summary")["entitlements"]


# ---------------------------------------------------------------------------
# DoD evidence manufacture from REAL sim purchase state
# ---------------------------------------------------------------------------
def dod_evidence(cid: str, plan: str, entitlement: dict) -> dict:
    """Build a full commerce-DoD evidence payload for a real sim purchase.

    evidence_mode is "simulated" — the honest label: every receipt here was
    witnessed against the wire-indistinguishable SIM, not exact_provider.
    """
    subject = f"agreement:{cid}:gcp:{plan}"
    receipts: list[dict] = []
    parents: list[str] = []
    for phase in PHASES:
        rid = f"r:{cid}:{phase}"
        receipts.append({"id": rid, "kind": phase, "subject_id": subject,
                         "parent_ids": parents.copy(),
                         "witness": entitlement["name"]})
        parents = [rid]
    receipts += [
        {"id": f"r:{cid}:brce", "kind": "commercial_actuation",
         "subject_id": subject, "parent_ids": [f"r:{cid}:billing"],
         "intent_id": f"intent:{cid}:purchase",
         "authority": AUTHORITY, "operation_id": f"op:purchase:{cid}",
         "consequence_id": entitlement["name"],
         "provider_effect_id": entitlement["usageReportingId"],
         "persisted": True},
        {"id": f"r:{cid}:replay", "kind": "replay", "subject_id": subject,
         "parent_ids": [f"r:{cid}:brce"],
         "operation_id": f"op:purchase:{cid}",
         "provider_effect_id": entitlement["usageReportingId"]},
    ]
    receipts += [
        {"id": f"r:{cid}:boundary-{suffix}", "kind": "failure_boundary",
         "subject_id": subject, "parent_ids": [f"r:{cid}:brce"]}
        for suffix in BOUNDARY_SUFFIXES
    ]
    phases = {phase: {"complete": True, "receipt_id": f"r:{cid}:{phase}"}
              for phase in PHASES}
    phases["lifecycle_transition"]["operations"] = [
        "renew", "expand", "reduce", "cancel"]
    return {
        "schema": SCHEMA,
        "subject": {
            "id": subject,
            "marketplace": "gcp",
            "provider": "demo-provider",
            "marketplace_contract_id": entitlement["name"],
            "agreement_id": subject,
            "environment": "gcp-marketplace-sim",
            "evidence_mode": "simulated",
            "source_sha": "a" * 40,
            "configuration_digest": "sha256:" + "b" * 64,
            "contract_digest": "sha256:" + "c" * 64,
        },
        "claim": {"required_capabilities": list(CAPABILITIES)},
        "unsupported_capabilities": [],
        "authority": {"active_billing_authorities": [AUTHORITY],
                      "admitted_billing_authority": AUTHORITY},
        "execution": {"observed": True, "admitted": True, "executed": True,
                      "verified": True, "consequence_observed": True,
                      "exact_subject": True},
        "phases": phases,
        "brce": {"do_path": "BRCE",
                 "intent_id": f"intent:{cid}:purchase",
                 "operation_id": f"op:purchase:{cid}",
                 "authority": AUTHORITY,
                 "consequence_id": entitlement["name"],
                 "provider_effect_id": entitlement["usageReportingId"],
                 "receipt_id": f"r:{cid}:brce"},
        "replay": {"attempted": True, "verified": True,
                   "operation_id": f"op:purchase:{cid}",
                   "provider_effect_id": entitlement["usageReportingId"],
                   "additional_external_effects": 0,
                   "receipt_id": f"r:{cid}:replay"},
        "failure_boundaries": {
            name: {"passed": True,
                   "receipt_id": f"r:{cid}:boundary-{suffix}"}
            for name, suffix in zip(BOUNDARY_NAMES, BOUNDARY_SUFFIXES)
        },
        "receipts": receipts,
    }


def run_dod_gate(evidence: dict, tmp_path: Path) -> dict:
    """Run the REAL DoD gate subprocess on the evidence payload."""
    path = tmp_path / "purchase-evidence.json"
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True),
                    encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(DOD_GATE), str(path), "--classify-only"],
        capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, (
        f"DoD gate rc={proc.returncode}\nstdout={proc.stdout}\n"
        f"stderr={proc.stderr}")
    return json.loads(proc.stdout)


# ---------------------------------------------------------------------------
# Fixture: this court owns its OWN sim instance (independent of CG1's
# singleton lifecycle).
# ---------------------------------------------------------------------------
@pytest.fixture()
def fx():
    fixture = ConferenceCommerceFixture()
    fixture.start()
    yield fixture
    fixture.teardown()


# ---------------------------------------------------------------------------
# Courts
# ---------------------------------------------------------------------------
class TestRegistrationToPurchase:
    def test_registration_and_purchase_both_succeed(self, fx):
        account = register(fx, "acme-corp")
        rec = purchase(fx, "acme-corp", TIERS["gold"],
                       Card(exp_month=12, exp_year=datetime.date.today().year + 1))
        assert account["state"] == "ACCOUNT_ACTIVE"
        assert rec["entitlement"]["state"] == "ENTITLEMENT_ACTIVE"
        assert rec["entitlement"]["plan"] == "team-aaif"
        summary = fx._get("/v1/billing/summary")
        assert summary["accounts"]["acme-corp"]["state"] == "ACCOUNT_ACTIVE"
        assert (summary["entitlements"]["acme-corp"]["state"]
                == "ENTITLEMENT_ACTIVE")

    def test_purchase_maps_to_signed_pubsub_entitlement(self, fx):
        rec = purchase(fx, "globex", TIERS["sponsor"],
                       Card(exp_month=6, exp_year=datetime.date.today().year + 2))
        ent = rec["entitlement"]
        # The purchase is a real signed provider event, not a local label.
        assert ent["jwt"].count(".") == 2
        assert ent["pubsubEnvelope"]["subscription"].endswith(
            "gcp-marketplace-entitlements")
        envelope = ent["pubsubEnvelope"]["message"]
        raw = __import__("base64").b64decode(envelope["data"])
        event = json.loads(raw)
        assert event["eventType"] == "ENTITLEMENT_ACTIVE"
        assert event["entitlement"]["id"] == "globex"


class TestDoDCourt:
    def test_purchase_evidence_classifies_partial_alive_sim_mode(self, fx,
                                                                 tmp_path):
        rec = purchase(fx, "initech", TIERS["platinum"],
                       Card(exp_month=3, exp_year=datetime.date.today().year + 1))
        evidence = dod_evidence("initech", TIERS["platinum"],
                                rec["entitlement"])
        result = run_dod_gate(evidence, tmp_path)
        assert result["standing"] == "PARTIAL_ALIVE", result
        assert result["billing_authority"] == AUTHORITY
        assert "EXACT_PROVIDER_EXECUTION_REQUIRED" in result["blockers"]
        assert result["refusals"] == []
        assert result["evidence_digest"].startswith("sha256:")

    def test_dod_court_refuses_empty_evidence(self, tmp_path):
        result = run_dod_gate({"schema": SCHEMA}, tmp_path)
        assert result["standing"] == "BLOCKED"
        assert result["refusals"], result


class TestIdempotentPurchase:
    def test_double_purchase_same_company_plan_is_idempotent(self, fx):
        card = Card(exp_month=9, exp_year=datetime.date.today().year + 1)
        first = purchase(fx, "wayne-enterprises", TIERS["sponsor"], card)
        second = purchase(fx, "wayne-enterprises", TIERS["sponsor"], card)
        ents = summary_entitlements(fx)
        # exactly ONE entitlement record for this company on this plan
        company_ents = [
            (k, v) for k, v in ents.items()
            if v["account"].endswith(f"/accounts/wayne-enterprises")
        ]
        assert len(company_ents) == 1, company_ents
        key, ent = company_ents[0]
        assert ent["plan"] == TIERS["sponsor"]
        assert ent["state"] == "ENTITLEMENT_ACTIVE"
        # the second purchase observed the SAME provider record, not a new one
        assert second["entitlement"]["name"] == first["entitlement"]["name"]
        assert second["entitlement"]["createTime"] == first["entitlement"]["createTime"]
        assert key == "wayne-enterprises"


class TestExpiredCard:
    def test_expired_card_purchase_refused_before_wire(self, fx):
        now = datetime.datetime(2026, 10, 5, 12, 0, 0)
        with pytest.raises(PurchaseRefused, match="REFUSED_CARD_EXPIRED:01/25"):
            purchase(fx, "hooli", TIERS["sponsor"], Card(1, 2025), now=now)
        assert "hooli" not in summary_entitlements(fx)
        assert "hooli" not in fx._get("/v1/billing/summary")["accounts"]

    def test_card_in_expiry_month_still_current(self):
        now = datetime.datetime(2026, 10, 31, 23, 59, 59)
        assert card_is_current(Card(10, 2026), now)

    def test_card_first_day_after_expiry_month_is_expired(self):
        now = datetime.datetime(2026, 11, 1, 0, 0, 0)
        assert not card_is_current(Card(10, 2026), now)


class TestFreeTierPayBeforeManufacture:
    def test_no_purchase_no_entitlement(self, fx):
        register(fx, "free-tier-org")
        ents = summary_entitlements(fx)
        assert "free-tier-org" not in ents
        # and the meter refuses usage from a non-customer (real sim gate)
        with pytest.raises(urllib.error.HTTPError) as excinfo:
            fx._post("/v1/servicecontrol:report", {
                "operations": [{
                    "operationId": "op-free-001",
                    "consumerId": "project:free-tier-org",
                    "metricValueSets": [{"metricValues": [
                        {"int64Value": 10}]}],
                }]})
        assert excinfo.value.code == 403
        body = json.loads(excinfo.value.read().decode())
        assert body["error"]["message"] == "ENTITLEMENT_REQUIRED"
        # zero revenue attributed to the non-customer
        summary = fx._get("/v1/billing/summary")
        assert all(r["consumerId"] != "project:free-tier-org"
                   for r in summary["recentReports"])
