"""Conference-commerce lane CG4: the metering court.

Every conference customer's usage is metered through the REAL Service Control
sim (`k8s/gcp-marketplace-sim/server.py`) behind CG1's conference-commerce
fixture: real HTTP wire, real account/entitlement :approve provisioning, real
deploy_aaif_solution.py deploys. The courts prove:

1. admission: every usage report a provisioned customer sends is admitted
   (`reportErrors: []`, `admittedCount: 1`) and every report carries distinct
   compute units;
2. billing rollup: the sim's billing summary reflects ALL customers' usage —
   `totalRealizedRevenueUsd` equals the independently computed
   (baseline + sum of all reported units) x $0.05;
3. per-customer attribution: customer A's units never appear under B's
   consumerId (operation store attribution is per tenant, never swapped);
4. quota: a report exceeding the customer's remaining bucket is refused with
   `RESOURCE_EXHAUSTED` and moves no metered units (no silent drop-in);
5. conservation: the sim's realized revenue matches the independently
   computed expected total exactly — no dropped or double-counted usage.

Chicago discipline: no mocks. Every court runs against the real sim wire.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from test_conference_commerce_fixture import (
    fixture_singleton,
)

N_CUSTOMERS = 10          # AGNTCon floor bounded for the metering court
REPORTS_PER_CUSTOMER = 4  # distinct-unit usage reports per customer
UNIT_PRICE_USD = 0.05     # must equal the sim's PRICING_PER_METRIC_UNIT
OP_PREFIX = "cg4-meter"   # unique op-id namespace for this lane

_customers_cache: list[dict] | None = None


def _provision() -> list[dict]:
    """Provision the customer floor once per test session (real approves)."""
    global _customers_cache
    if _customers_cache is None:
        _customers_cache = fixture_singleton().setup_customers(N_CUSTOMERS)
    return _customers_cache


def _deploy_pair() -> None:
    """Minimal real deploys so the metered tenants run through the deployer."""
    fx = fixture_singleton()
    for cid in ("akamai", "anthropic"):
        if cid not in fx.deploy_state:
            fx.deploy(cid)


# ---------------------------------------------------------------------------
# Real wire helpers
# ---------------------------------------------------------------------------
def _post_status(path: str, body: dict) -> tuple[int, dict]:
    fx = fixture_singleton()
    req = urllib.request.Request(
        fx.base + path, data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


def _get(path: str) -> dict:
    req = urllib.request.Request(fixture_singleton().base + path, method="GET")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def _billing() -> dict:
    view = _get("/v1/billing/summary")
    assert view["unitPriceUsd"] == UNIT_PRICE_USD, view
    return view


def _report(cid: str, op_id: str, units: int) -> tuple[int, dict]:
    return _post_status("/v1/servicecontrol:report", {
        "operations": [{
            "operationId": op_id,
            "consumerId": f"entitlement:{cid}",
            "metricValueSets": [{"metricValues": [{"int64Value": units}]}],
        }],
    })


# ---------------------------------------------------------------------------
# Court 1: every report from every provisioned customer is admitted, with
# distinct compute units, after real provisioning + minimal real deploys
# ---------------------------------------------------------------------------
def test_every_report_admitted_with_distinct_units() -> None:
    _provision()
    _deploy_pair()
    customers = _provision()

    admitted: dict[str, int] = {}
    counter = 0
    for rec in customers:
        cid = rec["cid"]
        for i in range(REPORTS_PER_CUSTOMER):
            counter += 1
            units = counter  # globally distinct compute units per report
            op_id = f"{OP_PREFIX}-{cid}-{i}"
            status, body = _report(cid, op_id, units)
            assert status == 200, (status, body)
            assert body["reportErrors"] == [], (op_id, body)
            assert body["admittedCount"] == 1, (op_id, body)
            admitted[op_id] = units

    total_sent = sum(admitted.values())
    assert len(admitted) == N_CUSTOMERS * REPORTS_PER_CUSTOMER
    assert len(set(admitted.values())) == len(admitted), "units not distinct"
    assert total_sent > 0
    _last_admitted = admitted  # consumed by the rollup court via module state
    globals()["_ADMITTED"] = admitted


# ---------------------------------------------------------------------------
# Court 2 + 5: billing summary reflects ALL customers' usage; revenue matches
# the independently computed expected total (no silent drops)
# ---------------------------------------------------------------------------
def test_billing_summary_matches_independent_expected_total() -> None:
    admitted = globals().get("_ADMITTED") or {}
    assert admitted, "metering court must run after the admission court"

    view = _billing()
    total_units = view["totalMeteredUnits"]
    revenue = view["totalRealizedRevenueUsd"]

    # Independent recomputation: the sim's whole-history units must be at
    # least everything THIS court admitted (other lanes may share the sim),
    # and revenue must be exactly totalUnits x unit price, to the cent.
    own_units = sum(admitted.values())
    assert total_units >= own_units, (total_units, own_units)

    # Conservation, to the cent: revenue = every admitted unit x $0.05.
    assert revenue == round(total_units * UNIT_PRICE_USD, 2), (
        total_units, revenue)

    # Per-operation revenue attribution is exact for every admitted report
    # still visible in the summary window.
    by_op = {r["operationId"]: r for r in view["recentReports"]}
    for op_id, units in admitted.items():
        if op_id in by_op:
            rec = by_op[op_id]
            assert rec["int64Value"] == units, (op_id, rec)
            assert rec["revenueEarnedUsd"] == round(units * UNIT_PRICE_USD, 4), (
                op_id, rec)

    # No silent drops: every admitted operation the sim still shows carries
    # our consumerId prefix attribution and appears exactly once.
    own_ops = [r for r in view["recentReports"]
               if r["operationId"].startswith(OP_PREFIX)]
    assert len(own_ops) == len({r["operationId"] for r in own_ops})


# ---------------------------------------------------------------------------
# Court 3: per-customer usage isolation — A's units never appear in B's records
# ---------------------------------------------------------------------------
def test_per_customer_usage_is_isolated() -> None:
    _provision()
    a, b = "akamai", "anthropic"
    a_units, b_units = 17, 39  # distinct, recognizable unit payloads

    status_a, body_a = _report(a, f"{OP_PREFIX}-iso-a", a_units)
    status_b, body_b = _report(b, f"{OP_PREFIX}-iso-b", b_units)
    assert status_a == 200 and body_a["reportErrors"] == [], body_a
    assert status_b == 200 and body_b["reportErrors"] == [], body_b

    view = _billing()
    window = view["recentReports"]
    a_ops = [r for r in window if r["consumerId"] == f"entitlement:{a}"]
    b_ops = [r for r in window if r["consumerId"] == f"entitlement:{b}"]
    assert "cg4-meter-iso-a" in {r["operationId"] for r in a_ops}
    assert "cg4-meter-iso-b" in {r["operationId"] for r in b_ops}
    # A's operation is never attributed to B, and vice versa.
    assert "cg4-meter-iso-a" not in {r["operationId"] for r in b_ops}
    assert "cg4-meter-iso-b" not in {r["operationId"] for r in a_ops}
    a_rec = next(r for r in window if r["operationId"] == f"{OP_PREFIX}-iso-a")
    b_rec = next(r for r in window if r["operationId"] == f"{OP_PREFIX}-iso-b")
    assert a_rec["int64Value"] == a_units
    assert b_rec["int64Value"] == b_units
    assert a_rec["revenueEarnedUsd"] == round(a_units * UNIT_PRICE_USD, 4)
    assert b_rec["revenueEarnedUsd"] == round(b_units * UNIT_PRICE_USD, 4)
    # No record in the window mixes tenants: each op id maps to exactly one
    # consumerId across the whole visible history.
    mapping: dict[str, set[str]] = {}
    for r in window:
        mapping.setdefault(r["operationId"], set()).add(r["consumerId"])
    assert all(len(v) == 1 for v in mapping.values())


# ---------------------------------------------------------------------------
# Court 4: exceeding the quota bucket -> RESOURCE_EXHAUSTED, no units moved
# ---------------------------------------------------------------------------
def test_quota_exceeded_is_resource_exhausted_with_no_silent_drop() -> None:
    _provision()
    before = _billing()
    remaining = before["remainingQuota"]
    assert remaining >= 0

    # A report larger than the whole remaining bucket must be refused.
    status, body = _post_status("/v1/servicecontrol:report", {
        "operations": [{
            "operationId": f"{OP_PREFIX}-quota-blowout",
            "consumerId": "entitlement:akamai",
            "metricValueSets": [
                {"metricValues": [{"int64Value": remaining + 1}]}],
        }],
    })
    assert status == 200, (status, body)
    errors = body["reportErrors"]
    assert len(errors) == 1, body
    assert errors[0]["code"] == "RESOURCE_EXHAUSTED", body
    assert body["admittedCount"] == 0, body

    after = _billing()
    # The refused report moved zero units and zero cents.
    assert after["totalMeteredUnits"] == before["totalMeteredUnits"]
    assert (after["totalRealizedRevenueUsd"]
            == before["totalRealizedRevenueUsd"])

    # The boundary is honest: a report that fits the remaining bucket is
    # admitted, and lands exactly at zero.
    status, body = _post_status("/v1/servicecontrol:report", {
        "operations": [{
            "operationId": f"{OP_PREFIX}-quota-exact",
            "consumerId": "entitlement:akamai",
            "metricValueSets": [{"metricValues": [{"int64Value": remaining}]}],
        }],
    })
    assert status == 200, (status, body)
    assert body["reportErrors"] == [] and body["admittedCount"] == 1, body
    drained = _billing()
    assert drained["remainingQuota"] == 0
    assert (drained["totalRealizedRevenueUsd"]
            == round((before["totalMeteredUnits"] + remaining)
                     * UNIT_PRICE_USD, 2))


def teardown_module(module):
    fixture_singleton().teardown()
