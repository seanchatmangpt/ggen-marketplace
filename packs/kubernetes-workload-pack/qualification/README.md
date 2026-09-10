# kubernetes-workload-pack/qualification

`orthogonal_scan.sh` runs the independent scanner layer described in
`../examples/control-mapping/control-map.md`'s "Orthogonal scanner layer"
section: kubeconform, Trivy config, Kyverno CLI, and Kubescape, each a
sensor that never sees this pack's own SPARQL gate (`gates/010_required.rq`).

```
brew install kubeconform trivy kyverno kubescape   # if not already installed
bash qualification/orthogonal_scan.sh
```

`policies/restricted-pss-subset.kyverno.yaml` is a real, runnable Kyverno
`ClusterPolicy` enforcing a subset of the Kubernetes Restricted Pod
Security Standard (no privileged containers, `allowPrivilegeEscalation:
false`, `capabilities.drop: ["ALL"]`, digest-pinned images) -- the layer
this pack's own gate 010 cannot express today (SEC-PRIV-001, SEC-IMG-001
in the control map), proven independently instead.

Cosign is deliberately not wired in here -- this pack generates
Deployment+Service YAML, not container images, so there is no real
image/digest to sign or verify (see the control map's SEC-COSIGN-001 row
for the honest scope boundary).
