# kubernetes-workload-pack/playground

A security-experimentation loop over `baseline.ttl` (a copy of
`../examples/high-assurance-workload/facts.ttl`), not scratch prose.
Learn the pack's actual admitted/refused security contract empirically
rather than by reading `ontology.ttl`/`gates/010_required.rq` cold.

## Loop

`ggen sync run` has no `--ontology` flag -- each working directory needs
its own `ggen.toml` declaring `[ontology].source` (this directory's own
`ggen.toml` already points at `baseline.ttl`, mirroring
`examples/minimal-secure-workload/`'s pattern):

```
cd playground
ggen sync run --dry-run                                 # 1. baseline: admitted (re-verified, real ggen, this session)
$EDITOR baseline.ttl                                     # 2. mutate one property (or copy into a fresh scenario dir)
ggen sync run --dry-run                                  # 3. observe: admitted or refused?
# 4. if refused, read the SPARQL gate's MESSAGE comments (gates/010_required.rq),
#    repair, regenerate, and compare against a scenario below.
```

## Scenarios (one mutation each, pre-built)

Each scenario is its own `ggen.toml` + `facts.ttl` directory (run
`cd scenarios/<name> && ggen sync run --dry-run`); all four results below
were re-run against the real `ggen` binary in this session.

| Scenario | Mutation from baseline | `ggen sync run --dry-run` result | Real Kubernetes-API-server result (live-verified, real `kind` cluster, this session) |
|---|---|---|---|
| `scenarios/missing-resources/` | Drops `resourceRequestsBlock`/`resourceLimitsBlock` | **REFUSED** (gate 010) | n/a -- never reaches the API server |
| `scenarios/privileged-container/` | Sets `privileged: true`, `allowPrivilegeEscalation: true` | **ADMITTED** (known gap -- gate 010 checks presence, not content of the raw securityContext block) | Applied as a **Deployment** against a namespace with PSA `enforce=restricted`: **still admitted**, `kubectl` prints the full violation list (`privileged`, `allowPrivilegeEscalation`, unrestricted capabilities, `runAsNonRoot`, missing `seccompProfile`) as a **warning only** -- PSA cannot reject at the Deployment object's own admission, only at the Pod object the Deployment controller later creates. `kubectl apply --dry-run=server` on this pack's generated Deployment YAML is therefore NOT sufficient evidence of PSA safety; corrected from an earlier, untested assumption in this same table. |
| `scenarios/mutable-image/` | Sets `image: "example/app:latest"` | **ADMITTED** (known gap -- `k8s:image` is an untyped string, no gate) | Passes API-server admission; the risk is supply-chain (no immutability guarantee), not something the API server itself refuses |
| `scenarios/legitimate-exception/` | Adds back exactly one capability (`NET_RAW`) with a stated rationale and compensating controls, everything else still Restricted-profile | **ADMITTED** (correctly -- this is the DfCM "secure default + explicit typed exception" pattern, not a violation) | Applied against the same `enforce=restricted` namespace: admitted with a PSA **warning** naming `NET_RAW` specifically (the one deliberate, documented deviation) -- confirms PSA is actually inspecting the capability list, not merely present, and that a scoped exception reads differently from the unrestricted violation set above. |

The two "known gap" rows are the same two files listed in
`../examples/negative-controls/README.md` -- this playground demonstrates
their *behavior*, that file documents their *status* against the control
map. See `../examples/control-mapping/control-map.md` (`SEC-PRIV-001`,
`SEC-IMG-001`, and its "Live cluster verification" section) for the full
real-cluster evidence and the candidate v0.2.0 fix.

## Known backlog (v0.2.0+), not yet covered by this pack

NetworkPolicy, RBAC (ServiceAccount/Role/RoleBinding), PodDisruptionBudget,
ResourceQuota, HorizontalPodAutoscaler, and a typed (non-raw-block)
capabilities/privileged model with a real refusal gate -- all still
hand-authored YAML in xaas's own `k8s/` today, or (for the typed
capabilities model) not built anywhere yet. Each is a real candidate for
its own template/gate in this pack, following the same admission-graph
shape as `010_required.rq`. These are CLUSTER_CONTROL/NAMESPACE_CONTROL
gaps in `../examples/control-mapping/control-map.md`'s terms, not silently
assumed -- a Fortune-5 workload built from this pack today needs its own
namespace-level NetworkPolicy/RBAC manifests alongside this pack's
generated Deployment+Service.
