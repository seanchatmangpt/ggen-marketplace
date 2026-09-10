# kubernetes-workload-pack/playground

Scratch space for trying k8s:Workload/k8s:Container facts before
committing a real `examples/` entry. Nothing here is load-bearing --
`ggen sync run --dry-run` should always be safe to run repeatedly.

Suggested flow:
1. Copy `../examples/xaas-workload.ttl` to `scratch.ttl` and edit freely
   (add a second container, drop a probe, change resource sizing).
2. `ggen sync run --dry-run --ontology scratch.ttl` from this directory
   and read the real rendered `k8s/<fileName>` output.
3. `kubectl apply --dry-run=client -f <rendered file>` against a real
   cluster context to confirm schema validity before promoting anything.
4. Promote what actually works to `../examples/`.

## Known backlog (v0.2.0+), not yet covered by this pack

NetworkPolicy, RBAC (ServiceAccount/Role/RoleBinding), PodDisruptionBudget,
ResourceQuota, HorizontalPodAutoscaler -- all still hand-authored YAML in
xaas's own `k8s/` today. Each is a real candidate for its own template in
this pack, following the same admission-graph shape as this one.
