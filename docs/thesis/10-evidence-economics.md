# Evidence economics, throughput, and coordination collapse

## 1. The economic problem changes when manufacture becomes cheap

Traditional software engineering assumes that implementation is expensive enough to dominate the cost structure. Under that regime, organizations optimize programmer utilization, project staffing, review meetings, ticket routing, and release coordination around scarce construction capacity.

Deterministic semantic manufacture changes the bottleneck. When a semantic change can fan out into many code, configuration, documentation, policy, and test consequences at low marginal construction cost, the system does **not** become costless. Scarcity moves.

The dominant scarce resources become:

- admissible semantic specification;
- evidence throughput;
- exception handling;
- authority for consequential transitions;
- external system latency;
- unresolved semantic conflict;
- proof/receipt recomputation.

The relevant economic question is therefore no longer “How many artifacts can developers write?” It is:

> **How much admitted change can the institution move to independently defensible standing per unit time and coordination cost?**

## 2. Throughput layers

Define four distinct throughputs.

### 2.1 Observation throughput `λ_O`

Rate at which candidate facts, requirements, events, changes, or defects enter the system.

### 2.2 Manufacturing throughput `λ_M`

Rate at which admitted subjects can be projected into candidate artifacts.

### 2.3 Evidence throughput `λ_E`

Rate at which manufactured subjects can acquire the receipts required for their intended standing.

### 2.4 Actuation throughput `λ_D`

Rate at which fully qualified subjects can cross consequential `DO` boundaries.

The system's sustainable delivery throughput is bounded by the minimum effective rate across required stages:

`λ_delivery ≤ min(λ_O-admitted, λ_M, λ_E, λ_D)`.

As `λ_M` increases dramatically, optimizing construction further yields little if `λ_E` or `λ_D` remains fixed.

## 3. Artifact count is a misleading productivity metric

A generated repository can create thousands of files or commits without increasing delivered value. Artifact count measures manufacturing activity, not evidence closure or external consequence.

A better accounting separates:

- **candidate artifacts**;
- **admitted artifacts**;
- **verified artifacts**;
- **actuated artifacts**;
- **durably standing artifacts**.

Let:

`Y = artifacts with required standing / manufactured artifacts`.

Call `Y` the **evidence yield**.

A system with enormous `λ_M` and low `Y` is an artifact factory with an evidence bottleneck. A system with high `Y` but low `λ_M` may still be construction-limited. The design target is not maximum raw generation; it is high semantic leverage with high evidence yield.

## 4. Little's Law for semantic manufacture

For each stable queue:

`L = λW`.

Apply separately.

### Construction queue

`L_M = λ_A W_M`

where admitted changes wait for manufacture.

### Evidence queue

`L_E = λ_M W_E`

where manufactured subjects wait for validation closure.

### Actuation queue

`L_D = λ_E W_D`

where qualified subjects wait for authority or external execution.

When manufacture becomes nearly instantaneous, `W_M → 0`, but the total lead time does not approach zero unless `W_E` and `W_D` also shrink.

This explains a characteristic post-generation failure mode: the repository appears hyperactive while validated WIP accumulates faster than it closes.

## 5. WIP should be measured in proof obligations, not only branches

A branch with one changed semantic fact may fan out into hundreds of artifacts but still represent one unresolved proof closure. Conversely, one small configuration change can invalidate many receipts and create large evidence WIP.

Define **proof WIP**:

`WIP_P = |open required proof obligations|`.

This may be more predictive of delivery latency than file count or commit count.

Examples of proof obligations:

- graph admits;
- pack qualifies;
- replay converges;
- target compiler accepts;
- integration consumer passes;
- policy check passes;
- deployment executes;
- external availability is observed.

The marketplace can eventually compute `WIP_P` from receipt dependency graphs.

## 6. Coordination as translation tax

Organizations pay coordination cost when the same intent is repeatedly translated between representations:

`requirement → ticket → design → code → config → test → docs → runbook → approval → deployment metadata`.

If each representation is independently authored, every semantic change creates a synchronization problem.

Let one domain fact be represented independently in `n` artifacts. Define pairwise synchronization edges in the worst case:

`E_sync = n(n-1)/2`.

Not every organization literally maintains all pairwise relationships, but the equation captures the combinatorial tendency: independent representations create potential disagreement edges.

Under single semantic authority plus deterministic projections:

`fact → {projection_1, ..., projection_n}`

coordination becomes star-shaped rather than clique-shaped. The number of authority relationships is approximately linear in the number of projections.

This is the core economic claim behind ontology-first manufacture: **remove synchronization work by removing independent representations, not by making humans coordinate them faster.**

## 7. Source singularity and state-space reduction

Consider one binary fact duplicated across `n` independently editable authorities. There are:

`2^n`

possible assignment states but only two globally consistent states when all copies are intended to agree.

The fraction of consistent states is:

`2 / 2^n = 2^(1-n)`.

This toy model is intentionally simple, but it illustrates why duplication is structurally dangerous: inconsistency opportunity grows exponentially with independent copies.

A deterministic projection architecture collapses the independently editable state space. It does not guarantee correctness of the source fact, but it removes a class of synchronization defects.

## 8. Semantic leverage

Define a semantic fact set `F` and consequence set `A`.

A simple leverage ratio is:

`L_s = |A_verified| / |F_authoritative|`.

Raw output count overstates leverage because repetitive boilerplate may have little semantic value. A more useful weighted version is:

`L_s^w = Σ value(a_i) / Σ maintenance_cost(f_j)`.

The values must be empirically defined for a study. Possible proxies include:

- independently testable interface fields;
- target systems reached;
- duplicated manual edits eliminated;
- review effort removed;
- defect opportunities removed.

High semantic leverage is the ability to change **one admitted meaning** and lawfully propagate it across many consequences.

## 9. Evidence amplification

Generation can amplify artifacts; receipts can amplify trust only when reusable.

Suppose one lower-level receipt proves an invariant shared by `k` higher-level claims. If exact dependency identities remain unchanged, reusing that receipt avoids `k` repeated validations.

Define receipt leverage:

`L_r = downstream proof obligations satisfied / receipt computations`.

Unsafe caching maximizes `L_r` by ignoring invalidation. A correct system maximizes `L_r` subject to evidence equivalence.

This turns incremental qualification into an economic optimization problem over a proof graph.

## 10. Marginal cost of a semantic change

For change `Δ`, define total cost:

`C(Δ) = C_spec + C_manufacture + C_evidence + C_exception + C_actuation + C_coordination`.

In conventional hand-maintained systems, `C_manufacture` and `C_coordination` may dominate.

In a mature semantic factory:

- `C_manufacture` approaches low deterministic compute cost;
- `C_coordination` shrinks because projections share authority;
- `C_evidence` becomes the major technical cost;
- `C_exception` dominates novel/unmodeled cases;
- `C_actuation` remains constrained by external systems and governance.

This is the economic signature of successful automation: cost does not disappear; it migrates from repeated construction to exceptions and evidence.

## 11. Human labor changes category

The architecture should not be described merely as “developers type less.” The more important transition is from **reconstruction labor** to **constitutional labor**.

Reconstruction labor includes:

- copying fields between formats;
- writing boilerplate adapters;
- manually synchronizing docs/config/code;
- rerunning known procedural steps;
- interpreting known validation rules repeatedly.

Constitutional labor includes:

- deciding which observations may be admitted;
- defining ontology and invariants;
- defining authority boundaries;
- adjudicating novel semantic conflicts;
- choosing evidence standards;
- changing policy when the current constitution is wrong.

A mature marketplace seeks to automate the former and make the latter explicit, inspectable, and progressively formalizable.

## 12. The coordination-collapse hypothesis

### H-CC1

For a class of repeated multi-representation engineering changes, replacing independent manual representations with one admitted semantic source plus deterministic projections reduces the number of human coordination interactions required per successfully validated change.

This is an empirical hypothesis.

### Measurement

Record for baseline and semantic-manufacture treatments:

- authoritative edit count;
- human handoff count;
- review-comment count attributable to representation drift;
- elapsed lead time;
- escaped inconsistency defects;
- total evidence cost.

The hypothesis is supported only if coordination falls without unacceptable increases in modeling/evidence cost.

## 13. The evidence-bottleneck hypothesis

### H-EB1

As manufacturing throughput increases while validator capacity remains approximately fixed, evidence WIP grows and total lead time becomes dominated by validation rather than construction.

This follows from queueing theory under stable assumptions but should be measured in the actual repository.

The operational response is not to slow manufacture arbitrarily. It is to:

- parallelize independent validation;
- improve failure localization;
- reuse valid receipts incrementally;
- generate negative controls automatically;
- move cheap constraints earlier;
- reserve expensive end-to-end courts for affected closures;
- increase deterministic self-verification in packs.

## 14. The exception-economy hypothesis

### H-EX1

After common manufacturing patterns become deterministic packs, human effort concentrates disproportionately in previously unseen exceptions, ambiguous admission, cross-pack semantic conflict, and novel authority decisions.

This predicts a heavy-tailed labor distribution: most routine changes approach negligible human construction cost while a small fraction of exceptions consume most expert attention.

If true, management should optimize for **exception resolution throughput**, not average typing throughput.

## 15. Transaction cost of evidence

Receipts are not free. They consume compute, storage, design effort, and sometimes operational latency.

Define evidence transaction cost:

`C_E = C_generate + C_store + C_verify + C_replay + C_invalidate`.

A proof is economically useful when the expected cost of defects, rework, audit, or unsafe actuation avoided exceeds its transaction cost, or when the proof is constitutionally mandatory regardless of immediate expected value.

The system should therefore tier evidence.

### Cheap early courts

- syntax;
- graph shapes;
- local invariants;
- path checks;
- static source policy.

### Medium courts

- ggen manufacture;
- replay;
- source non-mutation;
- target compile.

### Expensive courts

- cross-platform replay;
- full integration environment;
- real cloud deployment;
- independent third-party reconstruction;
- formal proof discharge.

The optimal pipeline rejects defects at the cheapest sound boundary that can observe them.

## 16. Cost of false standing

False positive evidence has asymmetric cost.

If a valid subject is temporarily blocked by an over-strict court, the cost is delay.

If an invalid or unauthorized subject receives `ALIVE` and crosses `DO`, the cost may include outage, security incident, corrupted state, or irreversible publication.

Therefore the loss function is asymmetric:

`Loss(false ALIVE) >> Loss(false BLOCKED)`

for high-consequence boundaries.

This justifies fail-closed admission near actuation while still allowing aggressive reversible construction upstream.

## 17. Construction maximalism, actuation minimalism

The economic optimum can be summarized as two opposing policies.

### Construction maximalism

Generate many reversible candidates cheaply. Explore alternatives. Materialize plans. Run simulations. Build artifacts before permission to deploy is required.

### Actuation minimalism

Cross external boundaries only with the minimum admitted authority and evidence closure needed for the intended consequence.

This is not contradictory. It is the separation that allows a high-throughput system to remain governable.

## 18. Time-to-information versus time-to-change

A deterministic factory has two important latencies.

`TTI` — time from observation to a manufactured/validated understanding of what would change.

`TTC` — time from observation to authorized external change.

Many systems force these together because they discover consequences only while actuating. DfCM-style reversible construction aims to minimize `TTI` independently of `TTC`.

Fast `TTI` is valuable even when governance intentionally keeps `TTC` slower. The organization can know exactly what would happen before granting authority for it to happen.

## 19. WIP closure as a marketplace product

Once evidence and process state are machine-readable, the marketplace can manufacture more than code. It can manufacture **closure decisions**.

Given repository activity, open branches, failed checks, dependency graphs, and receipts, a WIP scanner can classify work as:

- completed but unmerged;
- build-broken;
- blocked by external prerequisite;
- stale evidence;
- superseded;
- missing exact-head verification;
- abandoned/no longer connected to a current goal.

This turns Little's Law from retrospective management advice into an executable control loop.

## 20. System-level objective function

A simplistic objective such as “maximize commits” or “minimize build time” is easy to game.

A research-grade semantic factory should optimize a constrained objective such as:

`maximize  V_standing / (C_semantic + C_evidence + C_exception + C_coordination)`

subject to:

- authority constraints;
- replay constraints;
- security constraints;
- evidence validity;
- latency SLOs;
- resource budgets.

Where `V_standing` is the value of consequences that reached required standing, not raw generated volume.

The exact valuation is domain-specific, but the structure prevents activity from masquerading as throughput.

## 21. Phase-transition criterion

The architecture has crossed from “AI-assisted/manual software development” into a different manufacturing regime when most routine system change exhibits these properties:

1. intent enters as admitted semantic/process state rather than file-by-file instructions;
2. target artifacts are consequences, not independent work items;
3. construction throughput materially exceeds human review throughput;
4. validation and authority, not typing, dominate lead time;
5. evidence closure is computed incrementally from identity graphs;
6. humans spend most effort on exceptions and constitution changes;
7. process WIP can be reconstructed and closed mechanically;
8. artifact count ceases to be a meaningful measure of labor input.

This criterion is more useful than a threshold number of commits because it describes the **production function** of the ecosystem.

## 22. What would falsify the economics thesis?

The coordination/evidence thesis weakens if longitudinal data shows that:

- semantic modeling costs exceed the manual synchronization it replaces;
- exceptions are so frequent that most work never reaches reusable pack patterns;
- generated artifacts still require line-by-line human review at baseline rates;
- receipt production becomes more expensive than defect prevention/audit value;
- incremental evidence reuse proves too unsafe to deploy;
- pack composition creates more coordination than file-level development;
- human operators routinely bypass the authority constitution to meet latency needs;
- source singularity merely moves duplication into ontology adapters.

The economic case must therefore be measured, not inferred from high output volume.

## 23. Research consequence

The marketplace's deepest economic claim is not “code generation is faster.” Code generators have been fast for decades.

The stronger claim is:

> **When executable specifications become the unit of change, the organization can eliminate classes of representation-synchronization labor, move scarce human attention toward exceptions and constitutional decisions, and shift the system bottleneck from artifact construction to evidence and authorized actuation.**

That is a measurable change in the economics of software production. It is also the reason the evidence architecture is not optional: once construction cost collapses, verification becomes the factory.
