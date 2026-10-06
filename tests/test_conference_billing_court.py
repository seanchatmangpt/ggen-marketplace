"""CG6 conference-commerce lane: the billing rollup court.

The event's total revenue as an independently verified sum. The test IS the
invoice: ten AGNTCon customers meter known unit counts (100..1000) through the
real commerce sim's :report endpoint, then the sim's own billing summary
(`/v1/billing/summary`) is held against a sum computed in the test, not read
back from the sim.

Chicago discipline: real HTTP sim subprocess (via the CG1 fixture), real
account/entitlement approvals, real :report traffic. No mocks.

Imported collaborator (CG1): tests/test_conference_commerce_fixture.py
"""
from __future__ import annotations

import json
import urllib.request

import pytest

from test_conference_commerce_fixture import (
    CI_BOUND,
    ConferenceCommerceFixture,
    fixture_singleton,
)

PRICE = 0.05  # USD per metered unit (sim's PRICING_PER_METRIC_UNIT)

# Ten customers with known unit counts: 100, 200, ..., 1000. The customers
# are the first ten orgs of the CG1 conference floor (the named exhibitors).
UNIT_SCRIPT = [units for units in
               (100, 200, 300, 400, 500, 600, 700, 800, 900, 1000)]


def _report(fx: ConferenceCommerceFixture, cid: str, units: int,
            op_id: str) -> dict:
    """Send one real :report operation through the sim's service control."""
    body = {
        "operations": [{
            "operationId": op_id,
            "consumerId": f"entitlement:{cid}",
            "metricValueSets": [{
                "metricName": "aaif.conference.units",
                "metricValues": [{"int64Value": units}],
            }],
        }],
    }
    req = urllib.request.Request(
        fx.base + "/v1/services/aaif/consumers/x:report",
        data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def _summary(fx: ConferenceCommerceFixture) -> dict:
    with urllib.request.urlopen(fx.base + "/v1/billing/summary",
                                timeout=10) as resp:
        return json.loads(resp.read())


# ---------------------------------------------------------------------------
# Court 1: the empty case — a sim that has seen zero reports owes zero revenue
# ---------------------------------------------------------------------------
def test_zero_reports_zero_revenue() -> None:
    # A private sim instance (not the module singleton) so no other lane's
    # traffic can contaminate the empty baseline.
    fx = ConferenceCommerceFixture()
    try:
        fx.start()
        summary = _summary(fx)
        assert summary["totalOperations"] == 0
        assert summary["totalMeteredUnits"] == 0
        assert summary["totalRealizedRevenueUsd"] == 0.0
        assert summary["recentReports"] == []
    finally:
        fx.teardown()


# ---------------------------------------------------------------------------
# Court 2: the rollup — summary total equals the independently computed sum
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def billed():
    """Ten scripted customers, each approved then metered once."""
    fx = fixture_singleton()
    floor = fx.setup_customers(CI_BOUND)
    # The ten named conference orgs are the first ten of the floor.
    orgs = [r["cid"] for r in floor[:len(UNIT_SCRIPT)]]
    assert len(orgs) == len(UNIT_SCRIPT) == 10
    sent: list[dict] = []
    for i, (cid, units) in enumerate(zip(orgs, UNIT_SCRIPT)):
        assert any(r["cid"] == cid for r in floor), (
            f"scripted customer {cid} not on the conference floor")
        out = _report(fx, cid, units, op_id=f"bill-op-{i:02d}")
        assert out.get("reportErrors") == [], out
        assert out.get("admittedCount") == 1, out
        sent.append({"cid": cid, "units": units, "op_id": f"bill-op-{i:02d}"})
    yield fx, sent


def test_rollup_total_revenue_matches_independent_sum(billed) -> None:
    fx, sent = billed
    summary = _summary(fx)
    expected_units = sum(s["units"] for s in sent)
    expected_revenue = round(sum(s["units"] * PRICE for s in sent), 2)
    assert summary["totalMeteredUnits"] == expected_units  # 5500
    assert summary["totalRealizedRevenueUsd"] == pytest.approx(
        expected_revenue)  # 275.00
    assert summary["unitPriceUsd"] == PRICE
    # total operations == number of reports sent
    assert summary["totalOperations"] == len(sent) == 10


def test_per_account_revenue_matches_each_customers_units(billed) -> None:
    fx, sent = billed
    summary = _summary(fx)
    # The summary's entitlement records bind each customer id; every scripted
    # customer must be present and ACTIVE.
    entitlements = summary["entitlements"]
    for s in sent:
        ent = entitlements[s["cid"]]
        assert ent["state"] == "ENTITLEMENT_ACTIVE", ent
        assert ent["account"] == (
            f"providers/demo-provider/accounts/{s['cid']}")
    # Per-account revenue from the sim's own report records, grouped
    # independently in the test, must equal units x price per customer.
    by_consumer: dict[str, float] = {}
    for rec in summary["recentReports"]:
        key = rec["consumerId"]
        by_consumer[key] = by_consumer.get(key, 0.0) + rec["revenueEarnedUsd"]
    for s in sent:
        got = by_consumer.get(f"entitlement:{s['cid']}")
        assert got is not None, f"no report record for {s['cid']}"
        assert got == pytest.approx(round(s["units"] * PRICE, 4))
        # and the entitlement's usageReportingId was minted for this customer
        assert entitlements[s["cid"]]["usageReportingId"] == f"usage-{s['cid']}"


# ---------------------------------------------------------------------------
# Court 3: the recentReports window shows the MOST RECENT reports
# ---------------------------------------------------------------------------
def test_recent_reports_window_shows_most_recent(billed) -> None:
    fx, sent = billed
    # All ten scripted reports are currently the only traffic on the
    # singleton sim, so the window is exactly them, in send order...
    summary = _summary(fx)
    window = summary["recentReports"]
    assert [r["operationId"] for r in window] == [
        s["op_id"] for s in sent]
    # ...and the LAST window entry is the most recently sent report.
    assert window[-1]["operationId"] == sent[-1]["op_id"]
    # Recency proof: one more real report pushes the oldest out of the
    # ten-wide window while totals continue to accumulate (on the private
    # sim owned by this court, so the rollup totals above stay intact).
    probe = ConferenceCommerceFixture()
    try:
        probe.start()
        probe.approve_account("window-probe")
        probe.approve_entitlement("window-probe", "team-aaif")
        for i, units in enumerate([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]):
            out = _report(probe, "window-probe", units, f"probe-op-{i:02d}")
            assert out.get("reportErrors") == [], out
        psum = _summary(probe)
        assert psum["totalOperations"] == 11
        ids = [r["operationId"] for r in psum["recentReports"]]
        assert len(ids) == 10
        assert "probe-op-00" not in ids, "oldest report must fall off the window"
        assert ids[0] == "probe-op-01" and ids[-1] == "probe-op-10"
        assert psum["totalMeteredUnits"] == 66  # 1+..+11
    finally:
        probe.teardown()
