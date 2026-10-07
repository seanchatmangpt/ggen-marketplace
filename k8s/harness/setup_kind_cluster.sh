#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${1:-aaif-enterprise-court-cluster}"
CONFIG_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/kind-cluster-config.yaml"

echo "[INFO] Creating ephemeral kind cluster: ${CLUSTER_NAME}"
kind create cluster --name "${CLUSTER_NAME}" --config "${CONFIG_PATH}" --wait 60s

echo "[INFO] Cluster ${CLUSTER_NAME} initialized successfully."
kubectl cluster-info --context "kind-${CLUSTER_NAME}"
