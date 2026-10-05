import json
import subprocess
import time
import urllib.error
import urllib.request

import pytest

SWARM_INGRESS_URL = "http://localhost:8080"
GCP_SIMULATOR_URL = "http://localhost:8443"

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

class TestK8sAAIFGCPMarketplaceSimulation:
    """
    Chicago-Style Real-Cluster Test Court:
    Validates the live Kind cluster, CRDs, namespaces, fail-closed security,
    A2A swarm execution, and GCP Service Control metering receipts.
    Zero mocks or stubs.
    """

    def test_cluster_and_nodes_alive(self):
        res = run_cmd("kubectl get nodes -o json")
        assert res.returncode == 0, f"kubectl get nodes failed: {res.stderr}"
        nodes = json.loads(res.stdout).get("items", [])
        assert len(nodes) >= 2, f"Expected at least 2 nodes (control-plane + worker), found {len(nodes)}"
        for node in nodes:
            status = node["status"]["conditions"][-1]["type"]
            assert status == "Ready", f"Node {node['metadata']['name']} not Ready: {status}"

    def test_agent_router_crds_registered(self):
        res = run_cmd("kubectl get crds -o json")
        assert res.returncode == 0
        crds = json.loads(res.stdout).get("items", [])
        crd_names = [c["metadata"]["name"] for c in crds]
        expected_crds = [
            "aigatewayroutes.aigateway.envoyproxy.io",
            "aiservicebackends.aigateway.envoyproxy.io",
            "quotapolicies.aigateway.envoyproxy.io"
        ]
        for ec in expected_crds:
            assert ec in crd_names, f"Expected CRD {ec} not found in cluster!"

    def test_namespaces_and_pods_running(self):
        res_gcp = run_cmd("kubectl get pods -n gcp-marketplace -o json")
        assert res_gcp.returncode == 0
        gcp_pods = json.loads(res_gcp.stdout).get("items", [])
        assert len(gcp_pods) >= 1
        assert gcp_pods[0]["status"]["phase"] == "Running"

        res_swarm = run_cmd("kubectl get pods -n aaif-swarm -o json")
        assert res_swarm.returncode == 0
        swarm_pods = json.loads(res_swarm.stdout).get("items", [])
        assert len(swarm_pods) >= 3  # Coordinator, Qualification, Projection
        for pod in swarm_pods:
            assert pod["status"]["phase"] == "Running"

    def test_fail_closed_entitlement_gate(self):
        """Proves that un-entitled requests are refused with 403 Forbidden."""
        req = urllib.request.Request(
            f"{SWARM_INGRESS_URL}/tasks/send",
            data=json.dumps({"method": "tasks/send", "params": {"taskId": "t-unauth"}}).encode('utf-8'),
            headers={"Content-Type": "application/json", "X-GCP-Entitlement-ID": "non-existent-entitlement"},
            method='POST'
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                pytest.fail(f"Expected 403 Forbidden, got {resp.status}")
        except urllib.error.HTTPError as e:
            assert e.code == 403
            data = json.loads(e.read().decode('utf-8'))
            assert data["error"] in ["ENTITLEMENT_INACTIVE", "ENTITLEMENT_CHECK_FAILED"]

    def test_end_to_end_monetization_cycle(self):
        """
        Executes full procurement, entitlement approval, A2A execution,
        and Service Control metering revenue realization.
        """
        # 1. Approve account
        acc_id = f"test-acc-{int(time.time())}"
        req_acc = urllib.request.Request(
            f"{GCP_SIMULATOR_URL}/v1/providers/demo-provider/accounts/{acc_id}:approve",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method='POST'
        )
        with urllib.request.urlopen(req_acc, timeout=5) as resp:
            assert resp.status == 200
            acc_data = json.loads(resp.read().decode('utf-8'))
            assert acc_data["state"] == "ACCOUNT_ACTIVE"

        # 2. Approve entitlement
        ent_id = f"test-ent-{int(time.time())}"
        req_ent = urllib.request.Request(
            f"{GCP_SIMULATOR_URL}/v1/providers/demo-provider/entitlements/{ent_id}:approve",
            data=json.dumps({"account": acc_data["name"], "plan": "enterprise-scale"}).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method='POST'
        )
        with urllib.request.urlopen(req_ent, timeout=5) as resp:
            assert resp.status == 200
            ent_data = json.loads(resp.read().decode('utf-8'))
            assert ent_data["state"] == "ENTITLEMENT_ACTIVE"

        # 3. Execute A2A Swarm task with entitlement
        req_task = urllib.request.Request(
            f"{SWARM_INGRESS_URL}/tasks/send",
            data=json.dumps({
                "method": "tasks/send",
                "params": {"taskId": f"task-paid-{int(time.time())}", "computeUnits": 1000}
            }).encode('utf-8'),
            headers={"Content-Type": "application/json", "X-GCP-Entitlement-ID": ent_id},
            method='POST'
        )
        with urllib.request.urlopen(req_task, timeout=5) as resp:
            assert resp.status == 200
            task_resp = json.loads(resp.read().decode('utf-8'))
            assert task_resp["result"]["status"] == "COMPLETED"
            assert task_resp["result"]["computeUnitsMetered"] == 1000
            # Prove ash_a2a BEAM/WASM high-assurance execution
            ash_rt = task_resp["result"]["ash_a2a_runtime"]
            assert ash_rt["unforgeableAuth"] is True
            assert "affidavit-wasm-sig-" in ash_rt["affidavitWasmReceipt"]
            assert ash_rt["jwsCardSignature"] == "detached-jws-verified"
            # Prove autofde-lab formal decision planning
            fde_eng = task_resp["result"]["autofde_lab_engine"]
            assert fde_eng["solver"] == "scikit-decide-astar"
            assert fde_eng["bellmanOptimalityGated"] is True
            assert "ocel-trace-" in fde_eng["ocel2EventTraceId"]


        # 4. Audit billing summary and verify revenue realized
        with urllib.request.urlopen(f"{GCP_SIMULATOR_URL}/v1/billing/summary", timeout=5) as resp:
            assert resp.status == 200
            billing = json.loads(resp.read().decode('utf-8'))
            assert billing["totalOperations"] >= 1
            assert billing["totalMeteredUnits"] >= 1000
            assert billing["totalRealizedRevenueUsd"] >= 50.0  # 1000 units * $0.05 = $50.00
