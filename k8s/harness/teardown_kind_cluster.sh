#!/usr/bin/env bash
set -uo pipefail

CLUSTER_NAME="${1:-aaif-enterprise-court-cluster}"

echo "[INFO] Tearing down ephemeral kind cluster: ${CLUSTER_NAME}"
kind delete cluster --name "${CLUSTER_NAME}" || true
echo "[INFO] Ephemeral cluster ${CLUSTER_NAME} deleted cleanly."
