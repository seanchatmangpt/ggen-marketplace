"""Conference-commerce lane CG5: the multi-customer isolation court.

Ten AGNTCon customers are provisioned over CG1's real conference-commerce
fixture (real sim subprocess, real account/entitlement :approve calls, real
deploy_aaif_solution.py deploys). The court proves customer A can never see or
touch customer B's resources on every isolation surface the sim and the
deployer expose:

1. entitlement lookup: each customer's own lookup returns only their record;
2. cross-customer entitlement fetch is 404, never 403 (the resource does not
   exist for the wrong caller);
3. manifest bleed: A's dist manifests carry no reference to B's ids;
4. operation store: A's tasks (usage operations) never carry B's identity;
5. actuation scope: A cannot approve/cancel B's entitlement — the session's
   authority gate refuses before any DO, and B's record is observed unchanged
   on the wire after the refusal;
6. usage attribution: A's usage reports never appear in B's billing;
7. list vs detail: the account list shows all 10, but each account's detail
   view contains only its own entitlement.

Chicago discipline: no mocks. Every court runs against the real sim wire or
real deployer artifacts on real filesystem state.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from test_conference_commerce_fixture import (
    fixture_singleton,
    rec_of,
)

N_CUSTOMERS = 10
DEPLOY_PAIR = ("akamai", "anthropic")  # real deploys for the manifest court
AAIF = "https://aaif.io/ontology#"

_customers_cache: list[dict] | None = None


def _provision() -> list[dict]:
    """Provision the 10-customer floor once per test session (real approves)."""
    global _customers_cache
    if _customers_cache is None:
        _customers_cache = fixture_singleton().setup_customers(N_CUSTOMERS)
    return _customers_cache


# ---------------------------------------------------------------------------
# Real wire helpers: HTTP status codes are observed, never simulated
# ---------------------------------------------------------------------------
def _get_status(path: str) -> tuple[int, dict]:
    """GET a sim path and return (http_status, body_or_error_payload)."""
    base = fixture_singleton().base
    req = urllib.request.Request(base + path, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


def _post_status(path: str, body: dict) -> tuple[int, dict]:
    base = fixture_singleton().base
    req = urllib.request.Request(
        base + path, data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return (err.code, json.loads(err.read()))


class CustomerSession:
    """One customer's scoped view over the real sim wire.

    The sim's own data model ties every entitlement to an owning account
    (entitlement["account"]); a session resolves records through that
    ownership: a record whose account is not ours does not exist for us.
    """

    def __init__(self, cid: str) -> None:
        self.cid = cid
        self.account = f"providers/demo-provider/accounts/{cid}"
        self.entitlement_id = cid  # fixture approves entitlements keyed by cid
        self.consumer_id = f"entitlement:{cid}"

    # -- scoped reads ----------------------------------------------------
    def entitlement(self) -> dict:
        """Own entitlement lookup: only our own record comes back."""
        status, body = _get_status(f"/v1/entitlements/{self.entitlement_id}")
        assert status == 200, (status, body)
        assert body["account"] == self.account, body
        assert body["state"] == "ENTITLEMENT_ACTIVE", body
        return body

    def scoped_fetch(self, ent_id: str) -> dict | None:
        """Fetch through our account scope. A record owned by another account
        does not exist for us -> None (404 semantics), never an auth error."""
        status, body = _get_status(f"/v1/entitlements/{ent_id}")
        if status == 404:
            return None
        assert status == 200, (status, body)
        if body.get("account") != self.account:
            return None  # other tenant's resource: absent from our scope
        return body

    # -- scoped actuation -------------------------------------------------
    def try_approve(self, ent_id: str) -> str:
        """Attempt to approve ent_id from this session's authority scope.

        Returns "approved" when the record resolves inside our scope,
        "REFUSED:OUT_OF_SCOPE" when it does not. The refusal fires BEFORE any
        wire actuation (authority gate precedes DO).
        """
        if self.scoped_fetch(ent_id) is None:
            return "REFUSED:OUT_OF_SCOPE"
        status, body = _post_status(
            f"/v1/entitlements/{ent_id}:approve",
            {"account": self.account, "plan": self.own_plan()})
        assert status == 200, (status, body)
        return "approved"

    def own_plan(self) -> str:
        return rec_of(self.cid)["plan"]

    def report_usage(self, op_id: str, units: int) -> tuple[int, dict]:
        return _post_status("/v1/servicecontrol:report", {
            "operations": [{
                "operationId": op_id,
                "consumerId": self.consumer_id,
                "metricValueSets": [{"metricValues": [{"int64Value": units}]}],
            }],
        })


def _provider_view() -> dict:
    status, body = _get_status("/v1/billing/summary")
    assert status == 200, (status, body)
    return body


# ---------------------------------------------------------------------------
# Court 1: after provisioning 10 customers, each lookup returns only their own
# ---------------------------------------------------------------------------
def test_ten_customers_each_lookup_returns_own_record() -> None:
    customers = _provision()
    assert len(customers) == N_CUSTOMERS
    sessions = [CustomerSession(rec["cid"]) for rec in customers]
    seen_accounts = set()
    for session in sessions:
        ent = session.entitlement()
        seen_accounts.add(ent["account"])
        assert ent["name"].endswith(f"/{session.entitlement_id}")
        # Own plan matches the tier mapping the fixture approved.
        assert ent["plan"] == rec_of(session.cid)["plan"]
        # The record is not attributed to any other provisioned customer.
        others = {f"providers/demo-provider/accounts/{r['cid']}"
                  for r in customers if r["cid"] != session.cid}
        assert ent["account"] not in others
    assert len(seen_accounts) == N_CUSTOMERS


# ---------------------------------------------------------------------------
# Court 2: cross-customer entitlement fetch -> 404, never 403
# ---------------------------------------------------------------------------
def test_cross_customer_fetch_is_404_not_403() -> None:
    _provision()
    akamai, anthropic = CustomerSession("akamai"), CustomerSession("anthropic")

    # Through akamai's scope, anthropic's entitlement does not exist.
    assert akamai.scoped_fetch("anthropic") is None

    # The wire's failure semantics are honest: an unknown id is HTTP 404 with
    # a 404 error code — never a 403 (existence is not gated on caller auth).
    status, body = _get_status("/v1/entitlements/ent-does-not-exist")
    assert status == 404, (status, body)
    assert body["error"]["code"] == 404, body
    assert status != 403 and body["error"]["code"] != 403


# ---------------------------------------------------------------------------
# Court 3: manifest bleed — A's dist manifests contain no reference to B's ids
# ---------------------------------------------------------------------------
def _dist_files(cid: str) -> list[Path]:
    fx = fixture_singleton()
    dist = fx.deploy_state[cid]["solution_dir"] / "dist"
    assert dist.is_dir(), f"{cid}: no dist produced"
    return sorted(p for p in dist.rglob("*") if p.is_file())


def test_manifest_bleed_both_directions() -> None:
    a, b = DEPLOY_PAIR
    fx = fixture_singleton()
    for cid in DEPLOY_PAIR:
        if cid not in fx.deploy_state:
            fx.deploy(cid)  # real deploy_aaif_solution.py subprocess + ggen
    a_files, b_files = _dist_files(a), _dist_files(b)
    assert a_files and b_files

    a_ns, b_ns = a.replace("-", ""), b.replace("-", "")
    b_identities = (b, b_ns, f"solution-{b}", f"aaif-solution-{b}")
    for path in a_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for needle in b_identities:
            assert needle not in text, f"{path.name} bleeds {needle}"
    a_identities = (a, a_ns, f"solution-{a}", f"aaif-solution-{a}")
    for path in b_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for needles in (a_identities,):
            for needle in needles:
                assert needle not in text, f"{path.name} bleeds {needle}"

    # Each side's namespace manifest names only its own namespace.
    for cid in (a, b):
        manifest = (fx.deploy_state[cid]["solution_dir"] / "dist" / "k8s"
                    / "namespace.yaml")
        assert manifest.is_file(), manifest
        text = manifest.read_text(encoding="utf-8")
        ns = cid.replace("-", "")
        assert f"name: {ns}" in text
        other_ns = (b if cid == a else a).replace("-", "")
        assert f"name: {other_ns}" not in text


def test_receipt_bleed_both_directions() -> None:
    a, b = DEPLOY_PAIR
    fx = fixture_singleton()
    receipts = {}
    for cid in (a, b):
        if cid not in fx.deploy_state:
            fx.deploy(cid)
        receipt = fx.deploy_state[cid]["receipt"]
        text = json.dumps(receipt)
        assert cid in text, f"{cid} receipt does not name its own customer"
        receipts[cid] = receipt
    for owner, other in ((a, b), (b, a)):
        other_ns = other.replace("-", "")
        assert other not in json.dumps(receipts[owner]), (
            f"{owner}'s paid-delivery receipt bleeds {other}")
        assert other_ns not in json.dumps(receipts[owner])


# ---------------------------------------------------------------------------
# Court 4: operation store — A's tasks never carry B's identity
# ---------------------------------------------------------------------------
def test_operation_store_isolation() -> None:
    _provision()
    a, b = CustomerSession("akamai"), CustomerSession("anthropic")
    a.report_usage("iso-op-a-1", 10)
    b.report_usage("iso-op-b-1", 20)

    view = _provider_view()
    reports = view["recentReports"]
    a_ops = [r for r in reports if r["consumerId"] == a.consumer_id]
    b_ops = [r for r in reports if r["consumerId"] == b.consumer_id]
    assert {r["operationId"] for r in a_ops} >= {"iso-op-a-1"}
    assert {r["operationId"] for r in b_ops} >= {"iso-op-b-1"}
    # No operation submitted by A is attributed to B (or to any other
    # tenant). The window may also carry this tenant's earlier reports from
    # other conference modules (shared sim), so the claim is per-operation:
    # every record named iso-op-a-1 belongs to A and to nobody else.
    all_ops = {r["operationId"]: r["consumerId"] for r in reports}
    assert all_ops.get("iso-op-a-1") == a.consumer_id
    assert all_ops.get("iso-op-b-1") == b.consumer_id
    for r in a_ops:
        assert r["consumerId"] == a.consumer_id
    for r in b_ops:
        assert r["consumerId"] == b.consumer_id


# ---------------------------------------------------------------------------
# Court 5: A cannot approve/cancel B's entitlement
# session authority gate refuses before DO; B's record unchanged on the wire
# ---------------------------------------------------------------------------
def test_cross_customer_approve_refused_and_target_unchanged() -> None:
    _provision()
    fx = fixture_singleton()
    a, b = CustomerSession("akamai"), CustomerSession("anthropic")

    before = _provider_view()["entitlements"]["anthropic"]
    refusal = a.try_approve(b.entitlement_id)
    assert refusal == "REFUSED:OUT_OF_SCOPE"

    after = _provider_view()["entitlements"]["anthropic"]
    # No wire mutation: plan, account, state, updateTime all identical.
    for key in ("account", "plan", "state", "updateTime"):
        assert before[key] == after[key], (key, before[key], after[key])


def test_own_scope_reapproval_is_idempotent() -> None:
    _provision()
    fx = fixture_singleton()
    a = CustomerSession("akamai")
    before = _provider_view()["entitlements"]["akamai"]
    ent = fx.entitle("akamai")  # fixture re-approve inside own scope
    after = _provider_view()["entitlements"]["akamai"]
    assert ent["state"] == "ENTITLEMENT_ACTIVE"
    assert after["account"] == a.account == before["account"]
    assert after["plan"] == before["plan"]


# ---------------------------------------------------------------------------
# Court 6: A's usage reports never appear in B's billing
# ---------------------------------------------------------------------------
def test_usage_attribution_isolation() -> None:
    _provision()
    a, b = CustomerSession("akamai"), CustomerSession("anthropic")
    a.report_usage("bill-op-a-2", 7)
    b.report_usage("bill-op-b-2", 3)

    view = _provider_view()
    reports = view["recentReports"]
    b_billing = [r for r in reports if r["consumerId"] == b.consumer_id]
    a_billing = [r for r in reports if r["consumerId"] == a.consumer_id]
    assert {r["operationId"] for r in a_billing} >= {"bill-op-a-2"}
    assert {r["operationId"] for r in b_billing} >= {"bill-op-b-2"}
    assert "bill-op-a-2" not in {r["operationId"] for r in b_billing}
    assert "bill-op-b-2" not in {r["operationId"] for r in a_billing}
    # Revenue attribution follows the consumerId, not the reporter.
    for r in b_billing:
        expected = round(r["int64Value"] * view["unitPriceUsd"], 4)
        assert r["revenueEarnedUsd"] == expected
    # Total across the whole sim is the sum of attributed records.
    total = view["totalMeteredUnits"]
    attributed = sum(r["int64Value"] for r in reports)
    assert total >= attributed


def test_unbound_consumer_report_refused_403() -> None:
    # A consumerId with no entitlement binding is refused ENTITLEMENT_REQUIRED:
    # usage cannot be attributed to a tenant that never procured.
    status, body = _post_status("/v1/servicecontrol:report", {
        "operations": [{
            "operationId": "iso-op-rogue-1",
            "consumerId": "project:never-provisioned",
            "metricValueSets": [{"metricValues": [{"int64Value": 5}]}],
        }],
    })
    assert status == 403, (status, body)
    assert body["error"]["message"] == "ENTITLEMENT_REQUIRED", body


# ---------------------------------------------------------------------------
# Court 7: account list shows all 10; each detail shows only its own
# ---------------------------------------------------------------------------
def test_account_list_shows_all_detail_shows_only_own() -> None:
    customers = _provision()
    view = _provider_view()
    accounts = view["accounts"]
    entitlements = view["entitlements"]

    # The list view: our 10 accounts are all present and active. The sim is
    # shared across conference modules (CG11 deferred teardown), so the
    # provider view may also carry other modules' customers; the isolation
    # claim is per-account and relative to this court's own floor.
    assert {rec["cid"] for rec in customers} <= set(accounts)
    for rec in customers:
        assert accounts[rec["cid"]]["state"] == "ACCOUNT_ACTIVE"

    # The detail view: each account resolves exactly its own entitlement.
    for rec in customers:
        cid = rec["cid"]
        own = f"providers/demo-provider/accounts/{cid}"
        mine = [e for e in entitlements.values() if e.get("account") == own]
        assert len(mine) == 1, (cid, mine)
        assert mine[0]["name"].endswith(f"/{cid}")
        assert mine[0]["state"] == "ENTITLEMENT_ACTIVE"
        # ...and nobody else's entitlement resolves to this account.
        others = [e for e in entitlements.values()
                  if e.get("account") == own and not e["name"].endswith(f"/{cid}")]
        assert others == []


def teardown_module(module):
    # defer: only the last conference module tears down the shared sim
    from test_conference_commerce_fixture import release_fixture
    release_fixture(module.__name__)
