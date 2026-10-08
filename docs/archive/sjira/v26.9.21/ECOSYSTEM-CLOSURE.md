# Ecosystem closure — 2026-09-21

This is the human projection of `ECOSYSTEM-CLOSURE.ttl`. The RDF graph is canonical for this closure pass.

## Closure calculus

```text
sJira canonical WorkOrder
  -> ggen_igniter descriptor
  -> SA2A WorkEnvelope
  -> XaaS admission / lease
  -> zcode worker
  -> independent verifier
  -> receipt / replay
  -> sJira append-only standing
```

Identity conserved across the transport boundary:

```text
work_order_iri
+ checkpoint_iri
+ graph_digest
+ repository_identity
+ base_sha
```

No planner, UI, descriptor, lease, model, or workflow status is authority. Consequential DO remains BRCE-only.

## Current exact closure

| Subject | Exact head | Checkpoint standing | Next lawful edge |
|---|---|---|---|
| autofde-lab #170 | `cfe39b86...` | ALIVE | preserve; no more reasoning required |
| ggen-marketplace #475 | `1e9bb23b...` | ALIVE | reuse projection producer |
| ggen_igniter #20 | `3edd2ecb...` | REQUALIFYING | exact CI with warnings-as-errors + Chicago court |
| ggen_igniter #23 | `e20c5521...` | ALIVE | transport descriptor downstream |
| ggen_igniter #24 | `8032dab5...` | ALIVE | preserve admission/refusal court |
| ash_a2a #26 | `c6a4ddd3...` | ALIVE (GALL-029/030) | preserve focused court |
| ash_a2a #27 | `8d61f46e...` | ALIVE (transport) | consume exact tuple downstream |
| XaaS #60 | `7ee0da8a...` | REQUALIFYING | exact CI after compiler repair |
| zcode-cli #3 | `2ff7f595...` | ALIVE | preserve worker contract |
| ggen #720 | `0543d2c1...` | REQUALIFYING | exact replay court |
| ggen #725 | `e2a5e887...` | CANDIDATE | consumer manufacture proof |
| ash_surface #6 | `164a07ba...` | REQUALIFYING | exact CI + manufacture |
| mmdio #20 | `3a83644f...` | ALIVE (presentation projection) | keep broad lint baseline separate |
| zoela #25 | `3b6aeda7...` | UNKNOWN | fresh exact-head court |
| ash_planning_center #4 | `d3330797...` | UNKNOWN | fresh exact-head court |
| ash_kudzu #1 | `bbca3804...` | UNKNOWN | fresh exact-head court with retained evidence |
| beam4pm #84 | `4fd2deff...` | UNKNOWN | fresh recovery court; cancelled run is not evidence |

## Exclusions

This closure pass does **not** merge PRs, publish Hex/crates/npm artifacts, deploy applications, mutate live Jira SaaS, issue production leases, or infer downstream runtime standing from upstream tests.

Those are distinct authority/consequence transitions and require their own receipts.
