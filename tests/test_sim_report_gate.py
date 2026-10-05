"""AE2 finding 6: sim :report entitlement gate (Chicago style - real HTTP server).

Owner: security-fix lane (server.py / ConfigMap sync).
"""

import json
import threading
import urllib.request
import urllib.error
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "k8s" / "gcp-marketplace-sim")
)
import server  # noqa: E402

REPORT_URL = None


def setup_module(module):
    global REPORT_URL
    httpd = server.HTTPServer(("127.0.0.1", 0), server.ProductionGradeGCPHandler)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    REPORT_URL = f"http://127.0.0.1:{port}/v1/services/aaif.marketplace.googleapis.com:report"


def _report(consumer_id, units=10, op_id="op-test"):
    body = json.dumps({
        "operations": [{
            "operationId": op_id,
            "consumerId": consumer_id,
            "metricValueSets": [{
                "metricName": "aaif.marketplace.googleapis.com/agent_tokens",
                "metricValues": [{"int64Value": units}]
            }]
        }]
    }).encode()
    req = urllib.request.Request(REPORT_URL, data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def test_report_without_entitlement_refused_and_revenue_unchanged():
    server.USAGE_REPORTS.clear()
    before = len(server.USAGE_REPORTS)
    status, payload = _report("project:unregistered-client")
    assert status == 403
    assert payload == {"error": {"code": 403, "message": "ENTITLEMENT_REQUIRED"}}
    assert len(server.USAGE_REPORTS) == before  # revenue not counted


def test_report_with_seeded_entitlement_admitted_and_revenue_grows():
    server.USAGE_REPORTS.clear()
    status, payload = _report("project:demo-client-gcp", units=10)
    assert status == 200
    assert payload["reportErrors"] == []
    assert payload["admittedCount"] == 1
    assert len(server.USAGE_REPORTS) == 1
    assert server.USAGE_REPORTS[0]["revenueEarnedUsd"] == 0.5  # 10 * 0.05


def test_report_with_explicit_entitlement_form_admitted():
    server.USAGE_REPORTS.clear()
    status, payload = _report("entitlement:demo-ent-001")
    assert status == 200
    assert payload["admittedCount"] == 1


def test_report_decrements_quota_bucket():
    server.USAGE_REPORTS.clear()
    before = server.QUOTA_BUCKETS["default"]
    _report("project:demo-client-gcp", units=7)
    assert server.QUOTA_BUCKETS["default"] == before - 7
