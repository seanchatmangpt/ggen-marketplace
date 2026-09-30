# DfCM Pack

`dfcm-pack` is the executable source model for **Design for Combinatorial Maximalism** and the deployment calculus for the full Chatman ecosystem. It preserves the lawful option graph until admission makes an irreversible choice defensible; it is not an imperative "install everything" script.

## Governing sequence

`Preserve → Fence/Chesterton → Calculus → Exclusions → Falsifier → Extension → Operationalization`

The operational calculus is `parse → route → admit/refuse → diagnose/repair → construct → actuate → receipt → replay/hook → standing`. `SELECT`, `CONSTRUCT`, and `DO` are distinct. `DO` has one authority route: BRCE. Hooks manufacture intents and never actuate.

## Standing law

- `UNKNOWN` is not admitted.
- `UNSUPPORTED` is not `REFUSED`.
- `ALIVE` requires observed execution against the exact admitted subject plus a receipt.
- One failed edge changes topology; it does not invalidate the remaining lawful option graph.
- Generated artifacts begin at `UNKNOWN`; generation cannot self-promote them to runtime standing.
- Receipts bind source, base, authority, artifact, consequence, toolchain, environment, predecessor, replay identity, and standing; the generated runtime requires BLAKE3 for digest manufacture.
- Fortune-5 scale/SLO/resilience values are **targets**, never observations. They cannot self-crown readiness.

## Full Chatman deployment profile

The ontology carries `FullChatmanEcosystem` across deterministic manufacture, formal admission, process/workflow, gym/actuation, deterministic MCP, release, and publication surfaces. Existing release engineering remains fenced: `chatman-ecosystem-release-pack` publishes admitted consequences; it is not the deployment actuator.

## Fortune-5 readiness profile

`Fortune5Baseline` extends the same DfCM graph with an enterprise operating envelope rather than a separate checklist.

The baseline has **18 mandatory assurance domains** and **24 evidence-producing controls** covering:

- identity, zero trust, and independent authority domains;
- progressive change/release and receipted break-glass;
- cellular multi-region/multi-provider resilience and bounded blast radius;
- Tier-0 SLO/error budgets, RTO/RPO, DR exercises, and chaos;
- explicit capacity/stress envelopes with fail-closed overload behavior;
- metrics/logs/traces, incident evidence, forensic replay, and immutable audit;
- data classification/residency, tenant isolation, encryption, and key authority isolation;
- SBOM/provenance/signatures/dependency pinning;
- policy-as-code, cost/unit-economics guardrails, provider exit edges, and lifecycle/deprecation.

Independent authority domains may be machine authorities. Fortune-5 readiness does **not** reintroduce mandatory human approval: the law is separation of authority, exact admission, BRCE-only actuation, receipts, and replay.

### Baseline target envelope

These values are design/admission targets, not claims of achieved production performance:

- Tier-0 availability: `99.99%`
- error budget: `4.32 minutes / 30 days`
- RTO: `≤ 900s`
- RPO: `≤ 300s`
- resilience topology: `≥ 3 regions`, `≥ 3 zones/region`, `≥ 2 providers`
- maximum admitted blast radius: `≤ 5%`
- scale targets: `1,000,000 intents/s`, `100,000 concurrent workflows`, `10,000 receipted actuations/s`
- DR exercise cadence: `≤ 30 days`
- immutable evidence retention baseline: `2555 days` (baseline only; not a jurisdictional legal claim)


## CI optimization profile

`CIOptimizationProfile` applies the same DfCM topology to continuous integration. Its lexicographic objective is pull-request wall-clock to trustworthy green first, then main/merge wall-clock, then billed compute/network cost, while verification strength is preserved or increased.

The profile encodes **80/20 ERRC** rather than treating CI tuning as YAML cleanup:

- **Eliminate** duplicate compilation, dependency work, tool bootstrap, overlapping workflows, useless matrix combinations, irrelevant full-suite work, repeated container builds, and artifact round trips that cost more than recomputation.
- **Reduce** job/runner startups, network transfer, matrix cardinality, checkout surface, serial barriers, and redundant PR/main work.
- **Raise** cache-hit probability, incremental reuse, critical-path parallelism, signal per compute-second, safe baseline reuse, and runtime-balanced sharding.
- **Create** build-once/test-many only when it wins, precompiled tooling, deterministic caches, reusable workflows, dependency-aware change classification, fast/deep courts, prebuilt runner images, timing receipts, superseded-run cancellation, and runner selection by measured price-performance.

The generated agent contract treats **build-once/test-many as a falsifiable hypothesis**, not doctrine. Artifact movement must beat cached recomputation. Likewise, parallelism is admitted only when wall-clock saved exceeds runner startup, duplicated setup, and coordination cost.

Cache state never carries correctness authority. A cache miss must remain correct. Faster/cheaper claims are `UNKNOWN` until supported by exact-subject `OBSERVED`, `MEASURED`, or explicitly `ESTIMATED` evidence.

The intended steady state is that CI computes the **semantic delta introduced by the commit** instead of repeatedly manufacturing unchanged information.

## Manufactured consumer surface

`ggen sync` manufactures **34 coordinated projections** from the same graph.

### Core DfCM

1. `DFCM_DEPLOYMENT.md`
2. `DEPLOYMENT.toml`
3. `O.star.toml`
4. `OPTION_GRAPH.json`
5. `SELECT_LEDGER.json`
6. `BRCE_POLICY.json`
7. `RECEIPT_CONTRACT.json`
8. `REPLAY.md`
9. `deployment-state.json`
10. `STANDING.json`
11. `runtime.py`
12. `verify.py`
13. `formal/DfcmAdmission.lean`
14. `formal/MFACT.json`

### Fortune-5 enterprise projection

15. `enterprise/ENTERPRISE_READINESS.json`
16. `enterprise/CONTROL_CATALOG.json`
17. `enterprise/ASSURANCE_MATRIX.md`
18. `enterprise/SLO_POLICY.json`
19. `enterprise/RESILIENCE.toml`
20. `enterprise/CHANGE_CONTROL.json`
21. `enterprise/RELEASE_WAVES.json`
22. `enterprise/DATA_BOUNDARIES.json`
23. `enterprise/CAPACITY_ENVELOPE.toml`
24. `enterprise/SUPPLY_CHAIN.json`
25. `enterprise/AUDIT_POLICY.json`
26. `enterprise/INCIDENT_DR.md`
27. `enterprise/CHAOS_POLICY.json`
28. `enterprise/ENTERPRISE_INVARIANTS.json`
29. `enterprise/enterprise_verify.py`

### Post-AGI autonomous-agent projection

30. `enterprise/POST_AGI_READINESS.json`

### CI optimization projection

31. `ci/CI_OPTIMIZATION_AGENT.md`
32. `ci/CI_OPTIMIZATION_PROFILE.json`
33. `ci/CI_OPTIMIZATION_POLICY.json`
34. `ci/CI_OPTIMIZATION_RECEIPT.md`

The Fortune-5 verifier accepts supplied evidence only. `FORTUNE5_ALIVE` is refused without exact-subject observed/admitted/executed/verified state, receipt + replay, all controls, and explicit evidence for capacity, DR, supply chain, data boundaries, and the SLO window.

Marketplace qualification can establish deterministic graph load/manufacture/replay standing for these projections. It does **not** itself execute generated deployment programs, enterprise benchmarks, chaos experiments, DR exercises, formal proofs, or external actuators. Those boundaries remain `UNKNOWN` until their exact subjects execute and produce receipts.
