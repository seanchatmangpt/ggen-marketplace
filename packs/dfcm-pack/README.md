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

## v2.2.0 consolidation — one admission unit, sixteen modules, one court (2026-10-01)

The fourteen `dfcm-*` satellite packs were absorbed into this pack per the v26.9.30
consolidation wave (`docs/jira/v26.9.30/CONSOLIDATION-FRONTIER.md`, Tier-1 "dfcm family
15 → 1"). The satellite ontology already mapped five satellite namespaces with
`owl:equivalentClass` and machine-registered seven projection packs with
`dfcm:semanticOwner "dfcm-pack"`; this consolidation makes that registration physically
true. `ggen-combinatorial-maximalism-pack` intentionally remains a separate projection
(doctrine-referenced); its registry entry is unchanged.

Ruling made physical: the selection siblings carry **deliberately different algorithms** —
so the consolidation shares ontology/gates/court (one admission unit) and preserves every
algorithm verbatim as a family module under `families/<family>/` (scripts, queries,
templates, tests, shapes, python gates). Nothing algorithmic was rewritten.

### Layout

| path | content |
|---|---|
| `ontology/deployment.ttl` | the deployment/Fortune-5/CI law (formerly root `ontology.ttl`) |
| `ontology/option-capital.ttl` | canonical option-capital + compatibility map + projection registry |
| `ontology/<family>.ttl` | 14 satellite ontology modules, namespaces moved **verbatim** (no IRI changed) |
| `gates/*.rq` | 64 violation-row SELECTs with ORDER BY: 34 base + 30 family-prefixed (`dmc_ dmsc_ dsc_ dsea_ dsfc_ dsfe_ dspc_ dccp_ dfd_`) |
| `witnesses/{pass,fail}/<stem>.ttl` | exact-stem witness per gate (128 files) |
| `qualification/verify.py` | the ONE uniform exact-stem witness court (exit 0 = ADMITTED) |
| `qualification/fixtures/` | court fixtures (the five legacy JSON acceptance mocks retired: no consumer, mock subjects, not exact-subject evidence) |
| `families/<family>/` | satellite algorithms preserved verbatim (scripts/queries/templates/tests/shapes/python gates/docs) |
| `families/<family>.md` | satellite README preserved verbatim, or a synthesized family note where none existed |

### Uniform court semantics

For every gate: `union(ontology/*.ttl) + witnesses/pass/<stem>.ttl` must yield **zero rows**
(pass silent), and the standalone self-contained `witnesses/fail/<stem>.ttl` must yield
**at least one row** (fail fires). Fail-side deviation from the capability-ecology
precedent, recorded: dfcm's gate corpus is dominated by absence laws (fire when a required
fact is missing), which no additive witness can fire, so fail graphs are standalone minimal
worlds mined from each satellite court's own tests/expectations rather than union+additive.

### ggen wiring

`ggen.toml` now loads all 16 ontology modules (`[ontology] imports`) and enforces 63 of the
64 gates through real ggen (`[validation].gates`). `dfd_040_fortune5_closure` is
court-only: its count closure (exactly 50 required F5 controls) is satisfied by the
family fixture plane, not the bare union, and its pass witness re-injects the 50 verbatim
controls as the conservation witness.

### Recorded deviations (all minimal, all in owned paths)

1. ASK-form satellite gates converted to equivalent violation-row SELECTs (ggen admits
   refusal SELECTs only): `dmc_all_candidates_*`, `dmc_develop_no_do`,
   `dmc_experiment_realization`, `dmsc_010/020/030`, `dsea_01/02/03`, `dccp_01/02`.
   Positive-existence ASKs (dsea_01/02, dmc_experiment_realization) were converted to
   per-individual violation form; conversions are commented in each gate file.
2. `ORDER BY` appended to 26 base gates and all merged gates (strict-mode determinism; no
   semantic change).
3. `dfd_030_fortune5_required` and the duplicate-slug branch of `dfd_040_fortune5_closure`
   are population-scoped to the F5 control IRIs: the F5 vocabulary shares the
   `https://ggen.dev/ontology/dfcm#` control class with the base 29 C-controls, and the
   two well-formedness laws quantify over disjoint property sets.
4. The 50 F5 `EnterpriseControl` individuals moved verbatim from the satellite ontology to
   `families/full-deployment/fixtures/f5_controls.ttl` (family fixture plane, outside the
   union) for the same disjoint-population reason.
5. `sfe:SelectionRun` (a policy/exemplar individual typed as an execution run, carrying no
   subject) moved to `families/selection-frontier-execution/fixtures/selection_run.ttl`;
   stamping a fabricated SHA onto it to satisfy `dsfe_exact_subject` would be fabricated
   evidence.

### DfcmAdmission.lean template seam — resolved

Both this pack and `dfcm-full-deployment-pack` shipped `templates/DfcmAdmission.lean.tmpl`.
Canonical (kept, unchanged): **this pack's** — the strict superset (adds the `Status`
inductive, `authorityRoute` + `do_requires_brce`, `unsupported_ne_refused`,
`unknown_ne_alive`, `receipted`/`exactSubject` in `Evidence`/`Alive`, and a dynamic
`ecosystemComponents` count theorem). Superseded: full-deployment's leaner variant
(4-field `Evidence`, no Status/authorityRoute theorems, hard-coded `requiredComponents`
count = 12). Witness rerun after the consolidation: `ggen sync run` renders the canonical
template cleanly (`ecosystemComponents.length = 20`, dynamic), the 64-gate court is ALIVE,
and the full-deployment deployment-component population stays witnessed by
`dfd_010/020` (12 required components, complete property sets).

### Supersession

| absorbed pack (version) | namespace | module | family notes |
|---|---|---|---|
| `dfcm-explore-court-pack` (26.8.24) | `ex:` ggen.dev/ontology/dfcm-explore# | `ontology/explore-court.ttl` | `families/explore-court.md` |
| `dfcm-maximalist-court-pack` (26.8.24) | `dmc:` | `ontology/maximalist-court.ttl` | `families/maximalist-court.md` |
| `dfcm-maximalist-selection-control-pack` (26.8.24) | `dms:` | `ontology/maximalist-selection-control.ttl` | `families/maximalist-selection-control.md` |
| `dfcm-selection-capital-pack` (26.8.23) | `sel:` | `ontology/selection-capital.ttl` | `families/selection-capital.md` |
| `dfcm-selection-evidence-acquisition-pack` (0.1.0) | `dea:` | `ontology/selection-evidence-acquisition.ttl` | `families/selection-evidence-acquisition.md` |
| `dfcm-selection-falsifier-closure-pack` (0.1.0) | `chatman.ai/dfcm#` | `ontology/selection-falsifier-closure.ttl` | `families/selection-falsifier-closure.md` |
| `dfcm-selection-frontier-execution-pack` (26.8.24) | `sfe:` | `ontology/selection-frontier-execution.ttl` | `families/selection-frontier-execution.md` |
| `dfcm-selection-portfolio-consensus-pack` (26.8.24) | `dspc:` | `ontology/selection-portfolio-consensus.ttl` | `families/selection-portfolio-consensus.md` |
| `dfcm-candidate-compatibility-portfolio-pack` (0.1.0) | `seanchatman.dev/ontology/dfcm#` | `ontology/candidate-compatibility-portfolio.ttl` | `families/candidate-compatibility-portfolio.md` |
| `dfcm-explore-candidate-factory-pack` (0.1.0) | `.../dfcm/explore#` | `ontology/explore-candidate-factory.ttl` | `families/explore-candidate-factory.md` |
| `dfcm-explore-maximalist-pack` (26.8.24) | `.../dfcm/explore#` (shared IRI space with candidate-factory; additive union, SPARQL-safe) | `ontology/explore-maximalist.ttl` | `families/explore-maximalist.md` |
| `dfcm-full-deployment-pack` (26.8.14) | `dfcm:` ggen.dev (shared with deployment.ttl) | `ontology/full-deployment.ttl` | `families/full-deployment.md` |
| `dfcm-develop-maximalist-pack` (26.8.24) | `dev:` | `ontology/develop-maximalist.ttl` | `families/develop-maximalist.md` |
| `dfcm-dd-ui-pack` (26.8.18) | `ddui:` | `ontology/dd-ui.ttl` | `families/dd-ui.md` |

Superseded per pack: its `pack.toml` (absorbed into this manifest), its `ggen.toml`
generation wiring (queries/templates preserved as family modules; not re-wired — the
satellite generation queries predate strict-mode ORDER BY and stay verbatim), and its
per-pack court (replaced by the one uniform court above). Namespaces and individuals moved
verbatim; no IRI changed anywhere in this consolidation.
