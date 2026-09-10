# minimal-secure-workload

The smallest fact graph this pack admits (gate 010) that also clears the
Kubernetes Pod Security Standards **Restricted** profile floor at the
WORKLOAD_CONTROL layer:

- `runAsNonRoot: true`, `seccompProfile.type: RuntimeDefault` (pod-level)
- `allowPrivilegeEscalation: false`, `capabilities.drop: ["ALL"]` (container-level)
- explicit CPU/memory requests and limits (gate 010's OOM/CPU-throttle refusal)
- `automountServiceAccountToken: false` -- no ambient API-server credential
  unless a workload explicitly declares the need for one

Run it (re-verified against the real `ggen` binary in this session --
result: **ADMITTED**, `k8s/minimal-secure.yaml` planned for write):

```
cd examples/minimal-secure-workload
ggen sync run --dry-run
```

What this profile does **not** claim: NetworkPolicy enforcement, RBAC
scoping, PodDisruptionBudget, or any node/cluster/supply-chain control --
see `../control-mapping/control-map.md` for the explicit WORKLOAD vs
NAMESPACE/CLUSTER/NODE/SUPPLY_CHAIN/ORGANIZATIONAL/INHERITED boundary.
