# high-assurance-workload

A regulated-enterprise reference workload (`ledger-reconciler`) exercising
every WORKLOAD_CONTROL field this pack's v0.1.0 Deployment+Service scope
supports at the Kubernetes Restricted Pod Security Standard, plus
availability shape (3 replicas, HTTPS readiness/liveness probes) and a
digest-pinned (never `:latest`, never a mutable tag) image reference.

Run it (re-verified against the real `ggen` binary in this session --
result: **ADMITTED**, `k8s/ledger-reconciler.yaml` planned for write):

```
cd examples/high-assurance-workload
ggen sync run --dry-run
```

## What "high assurance" means here, precisely

This example is **NIST-control-mapped** and **assessment-ready evidence**
for the WORKLOAD_CONTROL layer only -- see
`../control-mapping/control-map.md` for the full NIST SP 800-53 Rev.5 /
SP 800-190 / CIS Kubernetes Benchmark / CISA-NSA hardening / Kubernetes
Restricted PSS mapping, and its explicit `known_gap` entries for every
NAMESPACE_CONTROL, CLUSTER_CONTROL, NODE_CONTROL, SUPPLY_CHAIN_CONTROL,
and ORGANIZATIONAL_CONTROL this manifest cannot itself satisfy (RBAC
scoping, NetworkPolicy enforcement, admission-controller policy,
node/control-plane hardening, image signature verification, SBOM,
vulnerability scanning, etcd-at-rest encryption, FIPS-validated crypto
modules).

This pack does **not** claim NIST certification, FedRAMP authorization,
FIPS validation, or STIG compliance for this example -- those are
organizational/assessor/system-boundary determinations, not properties a
Kubernetes manifest can establish on its own.
