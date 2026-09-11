# kubernetes-workload-pack/examples

Every subdirectory below is a self-contained `ggen.toml` + `facts.ttl`
project (the real consumption pattern this pack requires -- `ggen sync
run` has no `--ontology` flag; a project's `ggen.toml` declares
`[ontology].source` and pulls this pack in via `[packs]`).

- `xaas-workload/` -- the same k8s:Workload/k8s:Container shape this
  pack's first real consumer (`~/xaas`'s `k8s/deployment.yaml`) admits,
  reproduced standalone. Live-validated against a real `kind-xaas`
  cluster (RBAC scoped correctly, NetworkPolicy default-deny confirmed
  enforced, ResourceQuota confirmed enforced, etcd-at-rest encryption
  confirmed) in the session that produced this pack.

```
cd examples/xaas-workload
ggen sync run --dry-run
```

Expected: `k8s/deployment.yaml` planned for write, rendering a real
Deployment + Service pair with pod- and container-level securityContext,
resource requests/limits, envFrom ConfigMap+Secret refs, and readiness/
liveness probes.

## Security-graded examples

Added for a NIST/CIS/CISA-researched, control-mapped security baseline
(see `control-mapping/control-map.md` for full source provenance). Every
`ggen sync run --dry-run` result quoted below was re-run against the real
`ggen` binary in this session, not assumed:

- `minimal-secure-workload/` -- the smallest gate-010-admitted graph that
  also clears the Kubernetes Restricted Pod Security Standard floor.
  `ggen sync run --dry-run` → **ADMITTED**, `k8s/minimal-secure.yaml`.
- `high-assurance-workload/` -- a realistic regulated-enterprise workload
  exercising every WORKLOAD_CONTROL field this pack's v0.1.0 scope
  supports. `ggen sync run --dry-run` → **ADMITTED**,
  `k8s/ledger-reconciler.yaml`.
- `negative-controls/` -- deliberately invalid graphs, split honestly
  into gate-010-verified refusals and named, not-yet-enforced known gaps.
- `control-mapping/` -- the control map itself: NIST SP 800-53/800-190,
  CIS Kubernetes Benchmark, CISA/NSA hardening guidance, and Kubernetes
  Restricted PSS, mapped per-control to canonical fact, generated
  artifact, verification method, and explicit assessment-layer boundary
  (WORKLOAD/NAMESPACE/CLUSTER/NODE/SUPPLY_CHAIN/ORGANIZATIONAL).

See `../playground/` for a mutate-one-property experimentation loop over
the same baseline.
