# kubernetes-workload-pack/examples

`xaas-workload.ttl` is real, runnable, not illustrative prose: it's the
same k8s:Workload/k8s:Container shape this pack's first real consumer
(`~/xaas`'s `k8s/deployment.yaml`) admits, reproduced here standalone so
`ggen sync run` can be pointed straight at it.

Try it:

```
cd examples
ggen sync run --dry-run --ontology xaas-workload.ttl
```

Expected: `k8s/deployment.yaml` planned for write, rendering a real
Deployment + Service pair with pod- and container-level securityContext,
resource requests/limits, envFrom ConfigMap+Secret refs, and readiness/
liveness probes -- the same shape live-validated against a real
`kind-xaas` cluster (RBAC scoped correctly, NetworkPolicy default-deny
confirmed enforced, ResourceQuota confirmed enforced, etcd-at-rest
encryption confirmed) in the session that produced this pack.
