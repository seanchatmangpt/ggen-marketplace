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
  HTTP, port 8443, zero environment variables), plus the manifest and
  discovery documents it serves from `/app/*_discovery.json`.
- `k8s/aaif-swarm/aaif-swarm-mesh.yaml` — the AAIF mesh manifests.
- `k8s/kind-cluster-config.yaml` — the kind cluster shape. Port maps host
  8080 to NodePort 30080 and host 8443 to NodePort 30443.

All objects are namespaced. There are no cluster-scoped objects other than
the Namespace objects themselves.

## 1. Create the cluster

```bash
kind create cluster --config k8s/kind-cluster-config.yaml
```

## 2. Apply the simulator

```bash
kubectl apply -f k8s/gcp-marketplace-sim/gcp-procurement-simulator.yaml
kubectl wait --for=condition=available \
  deployment/gcp-marketplace-sim --timeout=90s
```

The in-cluster simulator serves on the NodePort mapped to host 8443. For
local deployer runs you can instead run `server.py` directly on the host as
shown in `tutorials/deploy-an-aaif-solution.md`.

## 3. Apply the AAIF mesh

```bash
kubectl apply -f k8s/aaif-swarm/aaif-swarm-mesh.yaml
```

## 4. Seed an approval

The simulator's entitlement check (`:check` / `:allocateQuota`, Service
Control operation shape) refuses unknown or inactive entitlements with
403 `ENTITLEMENT_INACTIVE`. Seed the simulator's approval store with the
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

An unknown entitlement fails closed with 403 `ENTITLEMENT_INACTIVE` before
any manufacture happens — pay-before-manufacture is the invariant, not an
optimization.

## 6. Tear down

```bash
kind delete cluster
```

## See also

- `tutorials/deploy-an-aaif-solution.md`
- `reference/aaif-deployer-contract.md`
- `explanation/aaif-commerce-seams.md`
