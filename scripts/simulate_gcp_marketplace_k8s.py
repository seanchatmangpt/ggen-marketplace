#!/usr/bin/env python3
"""
simulate_gcp_marketplace_k8s.py
Executes the end-to-end commercial realization loop on a live Kind Kubernetes cluster.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

CLUSTER_NAME = "aaif-marketplace-cluster"
SWARM_INGRESS_URL = "http://localhost:8080"
GCP_SIMULATOR_URL = "http://localhost:8443"

def run_cmd(cmd, check=True):
    print(f"[*] Executing: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and res.returncode != 0:
        print(f"[!] Command failed: {cmd}\nStderr: {res.stderr}\nStdout: {res.stdout}")
        sys.exit(res.returncode)
    return res

def wait_for_pods(namespace, timeout=120):
    print(f"[*] Waiting for pods in namespace '{namespace}' to be Ready...")
    start = time.time()
    while time.time() - start < timeout:
        res = run_cmd(f"kubectl wait --for=condition=Ready pods --all -n {namespace} --timeout=10s", check=False)
        if res.returncode == 0:
            print(f"[+] All pods in '{namespace}' are Ready!")
            return True
        time.sleep(3)
    print(f"[!] Timeout waiting for pods in {namespace}")
    return False

def setup_cluster():
    print("=== Step 1: Deploying Kubernetes Resources ===")
    # 1. Apply CRDs from vendored agent-router
    crd_dir = "vendors/agent-router/manifests/charts/ai-gateway-crds-helm/templates"
    for crd_file in sorted(os.listdir(crd_dir)):
        if crd_file.endswith(".yaml") and "crds" not in crd_file:
            path = os.path.join(crd_dir, crd_file)
            run_cmd(f"kubectl apply --server-side --force-conflicts -f {path}")

    # 2. Deploy GCP Marketplace Procurement Simulator
    run_cmd("kubectl apply -f k8s/gcp-marketplace-sim/gcp-procurement-simulator.yaml")

    # 3. Deploy AAIF Swarm Mesh
    run_cmd("kubectl apply -f k8s/aaif-swarm/aaif-swarm-mesh.yaml")

    # 4. Wait for deployments to be Ready
    wait_for_pods("gcp-marketplace")
    wait_for_pods("aaif-swarm")

def http_post(url, payload, headers=None):
    if headers is None:
        headers = {}
    headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))

def http_get(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))

def simulate_commercial_loop():
    print("\n=== Step 2: Running Commercial Realization Loop ===")

    # 1. Verify health
    s1, r1 = http_get(f"{GCP_SIMULATOR_URL}/healthz")
    print(f"[+] GCP Simulator Health: {s1} -> {r1.get('service')}")
    s2, r2 = http_get(f"{SWARM_INGRESS_URL}/healthz")
    print(f"[+] Swarm Coordinator Health: {s2} -> Role: {r2.get('agentRole')}")

    # 2. Customer buys SaaS plan via Google Cloud Marketplace
    account_id = "acc-western-digital-001"
    entitlement_id = "ent-aaif-swarm-prod-99"

    print(f"\n[*] 1. Approving Partner Account: {account_id}")
    s_acc, r_acc = http_post(f"{GCP_SIMULATOR_URL}/v1/providers/demo-provider/accounts/{account_id}:approve", {})
    print(f"    Account state: {r_acc.get('state')}")

    print(f"[*] 2. Activating Customer Entitlement: {entitlement_id}")
    s_ent, r_ent = http_post(f"{GCP_SIMULATOR_URL}/v1/providers/demo-provider/entitlements/{entitlement_id}:approve", {
        "account": r_acc.get("name"),
        "plan": "aaif-enterprise-swarm-tier"
    })
    print(f"    Entitlement state: {r_ent.get('state')}, reportingId: {r_ent.get('usageReportingId')}")

    # 3. Fail-Closed Test: Inactive / Bogus entitlement must be rejected
    print("\n[*] 3. Testing Fail-Closed Gate: Submitting A2A task with invalid entitlement...")
    s_bogus, r_bogus = http_post(
        f"{SWARM_INGRESS_URL}/tasks/send",
        {"method": "tasks/send", "params": {"taskId": "task-unauthorized"}},
        headers={"X-GCP-Entitlement-ID": "ent-bogus-999"}
    )
    print(f"    Expected 403 Forbidden: Got Status {s_bogus} -> {r_bogus.get('error')}")
    assert s_bogus == 403, f"Fail-closed admission breached! Got {s_bogus}"

    # 4. Admitted Execution & Metered Usage
    print("\n[*] 4. Submitting A2A Swarm Task under Active Entitlement...")
    s_exec, r_exec = http_post(
        f"{SWARM_INGRESS_URL}/tasks/send",
        {
            "method": "tasks/send",
            "params": {
                "taskId": "task-enterprise-codegen-042",
                "computeUnits": 500  # 500 compute/token units
            }
        },
        headers={"X-GCP-Entitlement-ID": entitlement_id}
    )
    print(f"    Execution status: {s_exec}")
    task_result = r_exec.get("result", {})
    print(f"    Task Status: {task_result.get('status')}, Metered Units: {task_result.get('computeUnitsMetered')}")
    print(f"    Service Control Receipt: {task_result.get('serviceControlReceipt')}")

    # 5. Financial Audit & Realized Revenue Verification
    print("\n[*] 5. Inspecting GCP Marketplace Realized Revenue Summary...")
    s_bill, r_bill = http_get(f"{GCP_SIMULATOR_URL}/v1/billing/summary")
    print(f"    Total Metered Operations: {r_bill.get('totalOperations')}")
    print(f"    Total Metered Units:      {r_bill.get('totalMeteredUnits')}")
    print(f"    Unit Price:               ${r_bill.get('unitPriceUsd')} / unit")
    print(f"    Total Realized Revenue:   ${r_bill.get('totalRealizedRevenueUsd')} USD")
    assert r_bill.get("totalRealizedRevenueUsd") > 0, "No revenue was earned!"
    print(f"\n[$$$] SUCCESS: Realized ${r_bill.get('totalRealizedRevenueUsd')} USD on Google Cloud Marketplace!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=["setup", "test", "cleanup", "all"], default="all")
    args = parser.parse_args()

    if args.action in ["setup", "all"]:
        setup_cluster()
    if args.action in ["test", "all"]:
        simulate_commercial_loop()
    if args.action == "cleanup":
        print(f"[*] Deleting Kind cluster {CLUSTER_NAME}...")
        run_cmd(f"kind delete cluster --name {CLUSTER_NAME}", check=False)
