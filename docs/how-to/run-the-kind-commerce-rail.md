# Run the local kind commerce rail

Use this guide to stand up the simulated GCP Marketplace commerce surface and
the AAIF actuation targets on a local kind cluster.

## Standing scope

The sim/kind rail is `PARTIAL_ALIVE`. Real GCP Marketplace procurement and
real GKE actuation are `BLOCKED` pending vendor onboarding. Everything below
is local simulation.

## Prerequisites

- Docker and `kind` installed.
- `kubectl` pointing at a kind context.
- This repository checked out at a known SHA.

## Rail anatomy

- `k8s/gcp-marketplace-sim/` — the commerce simulator: `server.py` (stdlib
  HTTP, port 8443; honors optional `AAIF_SIM_PORT` /
  `AAIF_SIM_DISCOVERY_DIR` overrides, no required environment variables),
  plus the manifest and discovery documents it serves from
  `/app/*_discovery.json` (delivered via the `gcp-procurement-simulator-code`
  ConfigMap).
- `k8s/aaif-swarm/aaif-swarm-mesh.yaml` — the AAIF mesh manifests.
- `k8s/kind-cluster-config.yaml` — the kind cluster shape. Port maps host
  8080 to NodePort 30080 and host 8443 to NodePort 30443.

All objects are namespaced. There are no cluster-scoped objects other than
the Namespace objects themselves.

## Network egress required at pod start

There is no Dockerfile under `k8s/`, so the simulator container is
`python:3.11-alpine` plus a startup command that runs
`pip install --quiet cryptography` at pod start. The pod **cannot** reach
readiness without outbound network access to PyPI; on an air-gapped or
egress-filtered cluster the Deployment will CrashLoop until egress exists.

## 1. Create the cluster

```bash
./k8s/harness/setup_kind_cluster.sh aaif-marketplace-cluster
```

The script's `--name` argument is authoritative: `kind-cluster-config.yaml`
intentionally carries no `name:` so the two can never disagree. Use the same
name with `k8s/harness/teardown_kind_cluster.sh` afterwards.

## 2. Apply the simulator

```bash
kubectl apply -f k8s/gcp-marketplace-sim/gcp-procurement-simulator.yaml
kubectl wait --for=condition=available \
  deployment/gcp-procurement-simulator --timeout=90s
```

The in-cluster simulator serves on the NodePort mapped to host 8443. For
local deployer runs you can instead run `server.py` directly on the host as
shown in `tutorials/deploy-an-aaif-solution.md`.

## 3. Apply the AAIF mesh

```bash
kubectl apply -f k8s/aaif-swarm/aaif-swarm-mesh.yaml
```

## 4. Seed an approval

The simulator's usage-report gate (`:report`, Service Control operation
shape) refuses a `consumerId` that does not resolve to an active
entitlement with 403 `ENTITLEMENT_REQUIRED`. Seed the simulator's
entitlement store (via `POST /v1/providers/demo-provider/entitlements/`
...`:approve`, or `/accounts/...:approve` for account approval) with the
entitlement id your deployer run will present. Consult
`k8s/gcp-marketplace-sim/server.py` for the exact in-memory store shape —
do not rely on a copied seed snippet here.

## 5. Drive the rail

With the entitlement id exported:

```bash
export AAIF_ENTITLEMENT_ID=ent-acme-001
export AAIF_ENTITLEMENT_ENDPOINT=http://localhost:8443
python3 scripts/deploy_aaif_solution.py solutions/acme --target kind
```

A successful run shows an admitted service-control receipt (admitted count
and revenue fields) plus the paid-delivery receipt appended to
`receipts/paid-delivery/chain.jsonl`.

An unknown entitlement fails closed with 403 `ENTITLEMENT_REQUIRED` at
`:report` before any manufacture happens — pay-before-manufacture is the invariant, not an
optimization.

## 6. Tear down

```bash
kind delete cluster
```

## See also

- For the scripted end-to-end loop without k8s, see `scripts/run_solution_quickstart.py`
- `tutorials/deploy-an-aaif-solution.md`
- `reference/aaif-deployer-contract.md`
- `explanation/aaif-commerce-seams.md`
