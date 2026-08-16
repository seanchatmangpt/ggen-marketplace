# Defense dossier: claims, evidence, falsifiers, and proof debt

## 1. Purpose

A dissertation defense should not require the reader to reconstruct the thesis from hundreds of pages. This chapter is the **claim ledger** for the monograph. Every major claim is reduced to:

- the proposition being defended;
- the mechanism that could make it true;
- the evidence currently admissible;
- the strongest known falsifier;
- the remaining proof or experiment debt.

The dossier intentionally includes incomplete claims. A research system earns credibility by exposing what is not yet proved.

## 2. Claim classes

Claims are classified as:

- **constitutional** — rules the system chooses to enforce;
- **formal** — statements derived from definitions under assumptions;
- **implementation** — statements about repository/runtime behavior;
- **empirical** — statements requiring measurement across episodes/populations;
- **economic** — statements about cost, throughput, coordination, or labor distribution;
- **security** — statements about capability, integrity, or adversarial behavior.

A constitutional rule can be valid policy without being a scientific discovery. An implementation can conform to a rule without proving the rule is economically optimal. These categories must remain separate.

## 3. Thesis T1 — semantic source singularity

### Claim

For classes of multi-representation software change, one admitted semantic authority plus deterministic projections reduces synchronization state and can reduce human coordination compared with independently maintained representations.

### Mechanism

`semantic fact → deterministic projections`

replaces:

`representation_1 ↔ representation_2 ↔ ... ↔ representation_n`.

### Formal support

The state-space proposition in the theorem/economics chapters shows that independent duplicate authorities admit inconsistent states that disappear when one source controls projections.

### Implementation evidence

The mdBook experiment models navigation in `docs/book.ttl` and projects `docs/SUMMARY.md` rather than maintaining both independently.

### Falsifier

Longitudinal studies show semantic source requires more coordination/maintenance than direct duplicated files, or generated artifacts still require independent edits often enough that source singularity is nominal only.

### Proof debt

- empirical maintenance study against hand-maintained and structured-template baselines;
- drift incident dataset;
- measure authoritative edit count and reviewer coordination per change.

### Standing

**PARTIAL_ALIVE as empirical thesis; ALIVE for demonstrated mdBook source-singularity mechanism.**

## 4. Thesis T2 — deterministic semantic manufacture

### Claim

For an exact complete subject, ontology/query/template manufacture can behave as a deterministic compiler projection whose consequences converge under replay.

### Mechanism

`S = (identity, G, Q, T, V, E)`

`A = μ(S)`.

### Formal support

Functional determinism follows if `μ` is a function over a complete subject. Replay mismatch exposes either implementation impurity, incomplete subject modeling, or an underspecified equivalence relation.

### Implementation evidence

Marketplace pack qualification exercises real ggen manufacture and replay for admitted packs; deterministic catalog/archive courts compare reconstructed consequences.

### Falsifier

An exact subject under a declared environment class produces non-equivalent specified artifacts on replay.

### Proof debt

- R3–R5 independent reproducibility studies;
- canonical graph/digest semantics for semantic-equivalence claims;
- explicit hidden-input perturbation suite.

### Standing

**ALIVE for exercised exact-head qualification/replay boundaries; UNKNOWN beyond observed replay classes.**

## 5. Thesis T3 — evidence must be boundary-scoped

### Claim

A system represents truth more accurately when success/failure evidence is attached to exact boundaries rather than collapsed into one repository-level green/red status.

### Mechanism

Receipt DAG + claim-specific standing:

`σ(claim, receipts, time)`.

### Formal support

Local failure preservation theorem: failure at independent boundary `b2` does not negate a predicate already established at `b1`.

### Implementation evidence

The first self-hosting Pages run provided a natural experiment: generic marketplace CI and vacuity audit succeeded while root self-hosting manufacture failed on `FM-CONFIG-101`. The evidence model retained both facts and localized the repair to the consumer configuration.

### Falsifier

Boundary-scoped evidence repeatedly causes operators to misdiagnose system health or proves too complex to improve decisions relative to ordinary CI status.

### Proof debt

- executable receipt DAG;
- standing derivation engine;
- user study or operational MTTR comparison against untyped CI failure reporting.

### Standing

**ALIVE as demonstrated failure-localization mechanism; empirical productivity advantage remains OPEN.**

## 6. Thesis T4 — exact-subject law

### Claim

Evidence is admissible for a software subject only when the executed immutable source identity equals the claimed identity or a claim-complete equivalence proof exists.

### Mechanism

Exact checkout + identity assertion before crown-bearing execution.

### Formal support

Exact-subject necessity theorem.

### Implementation evidence

The marketplace workflows assert the checked-out commit against the subject SHA before execution of crown-bearing courts.

### Falsifier

A workflow can silently validate a different immutable tree while still satisfying the exact-subject guard, or the receipt omits identity needed to distinguish subjects.

### Proof debt

- bind tree identity in addition to commit where useful;
- signed/content-addressed receipt representation;
- negative-control workflow deliberately attempting mismatch.

### Standing

**ALIVE for current workflow assertion behavior; stronger signed receipt binding remains OPEN.**

## 7. Thesis T5 — SELECT/CONSTRUCT/DO separation

### Claim

Separating reversible construction from consequential actuation permits aggressive candidate generation without granting construction ambient production authority.

### Mechanism

`SELECT → CONSTRUCT → VERIFY → DO`

with phase-specific capability sets.

### Formal support

Capability-exclusion theorem and construction/actuation optionality proposition.

### Implementation evidence

The Pages workflow builds on pull requests but upload/deployment actuators are main-only; PR validation can establish book-build standing without public deployment authority.

### Falsifier

Construction contexts can directly invoke consequential mutation through available capabilities, or real operations require such broad authority that the separation is routinely bypassed.

### Proof debt

- explicit capability graph;
- automated authority-policy validation;
- adversarial confused-deputy tests;
- systematic secret/remote-write absence receipts.

### Standing

**ALIVE for the mdBook PR/deploy separation; broader ecosystem claim remains PARTIAL_ALIVE.**

## 8. Thesis T6 — self-hosting is stronger integration evidence

### Claim

A marketplace-critical pack that manufactures a real piece of marketplace infrastructure provides stronger integration evidence than a synthetic fixture alone.

### Mechanism

`marketplace distributes P`

and

`marketplace infrastructure consumes P`.

### Implementation evidence

The mdBook pattern-language pack manufactures the marketplace's own book control surface, which is then accepted by the independent mdBook target compiler.

### Falsifier

Self-hosting fixtures become so coupled to implementation details that they stop detecting defects or systematically conceal incompatibilities external consumers experience.

### Proof debt

- external consumer population;
- compare defect discovery between synthetic qualification and self-hosting;
- prevent self-hosting consumer from introducing pack-specific backdoors.

### Standing

**ALIVE for current mdBook self-hosting build boundary; general predictive superiority remains EMPIRICAL/OPEN.**

## 9. Thesis T7 — typed refusal improves repairability

### Claim

Typed, localizable refusal reduces diagnostic entropy and can reduce repair lead time compared with generic failure.

### Mechanism

`REFUSED:<domain>:<predicate>` partitions the failure space.

### Formal support

A finer failure partition contains more diagnostic information than one undifferentiated failure value.

### Falsifier

Typed codes do not reduce repair time, are routinely wrong, or impose maintenance cost larger than their diagnostic value.

### Proof debt

- seeded-failure experiment;
- MTTR comparison;
- refusal precision/confusion matrix;
- stable code taxonomy.

### Standing

**DERIVED for information partitioning; empirical MTTR claim UNKNOWN.**

## 10. Thesis T8 — pack composition can become algebraic

### Claim

A useful subset of packs can compose under a partial operator with explicit graph, target, dependency, toolchain, evidence, and authority compatibility predicates.

### Mechanism

`⊗ : Pack × Pack ⇀ Pack`.

### Formal support

Pack-algebra chapter defines conditional associativity, local independence/commutativity, target ownership, refinement, supersession, and receipt invalidation closure.

### Falsifier

Real pack interactions require ad-hoc global side effects so frequently that compatibility predicates cannot remain local or compositional.

### Proof debt

- machine-readable target ownership;
- typed dependency edges;
- authority join policy;
- cross-pack fixtures;
- mechanized associativity for admitted pure subset.

### Standing

**FORMAL DESIGN / MECHANIZATION CANDIDATE; implementation PARTIAL_ALIVE.**

## 11. Thesis T9 — incremental evidence reuse can safely reduce validation cost

### Claim

If proof dependencies are complete and exact identities are unchanged, prior receipts outside the changed dependency closure can be reused without re-execution.

### Mechanism

`invalidate(Δ) = Reachable_R(Δ)`.

### Formal support

Graph reachability over proof dependencies.

### Falsifier

A reused receipt is later shown invalid because an unmodeled dependency changed, or dependency tracking costs exceed saved validation work.

### Proof debt

- complete dependency graph extraction;
- claim-relative equivalence policy;
- stale-receipt negative controls;
- false-reuse incident monitoring.

### Standing

**OPEN implementation hypothesis.**

## 12. Thesis T10 — evidence becomes the bottleneck after construction collapses

### Claim

When manufacturing throughput increases materially faster than validation/actuation throughput, evidence WIP dominates total delivery lead time.

### Mechanism

Little's Law applied separately to manufacture, evidence, and actuation queues.

### Formal support

Under stable queue assumptions, increasing arrival/production rate with fixed service capacity increases WIP/lead time pressure.

### Falsifier

Measured repositories remain construction-limited despite very high automated manufacture, or evidence work scales automatically enough that no persistent evidence queue forms.

### Proof debt

- longitudinal event log;
- queue classification;
- observed `λ_M`, `λ_E`, `λ_D`, `L`, and `W`;
- before/after comparison as deterministic pack coverage expands.

### Standing

**THEORETICALLY MOTIVATED, EMPIRICALLY OPEN.**

## 13. Thesis T11 — coordination can collapse from clique to star

### Claim

When many representations share one semantic authority, synchronization relationships can become star-shaped projections instead of independent pairwise coordination.

### Mechanism

Independent model:

`E_sync ≈ n(n-1)/2`.

Projection model:

`E_projection ≈ n`.

### Falsifier

Adapters and ontology governance reintroduce equivalent pairwise coordination, or the semantic source becomes a universal bottleneck requiring the same communication load.

### Proof debt

- empirical handoff/coordination graph;
- representation-change study;
- ontology-governance cost measurement.

### Standing

**DERIVED as structural toy model; organizational claim OPEN.**

## 14. Thesis T12 — receipts can become a content-addressed evidence fabric

### Claim

Structured receipts bound to immutable identities can support standing derivation, provenance audit, incremental invalidation, and release reconstruction more reliably than ephemeral unstructured CI badges/logs alone.

### Mechanism

Receipt DAG + content identity + policy-versioned standing derivation.

### Prior-art alignment

PROV-O, in-toto, SLSA provenance, Git identity, and reproducible-build practice provide substantial foundations. The marketplace-specific problem is integrating semantic manufacture, typed boundary standing, and actuation authority.

### Falsifier

Receipt capture omits too much context, cannot be canonicalized/verified economically, or duplicates existing attestation systems without additional operational value.

### Proof debt

- interoperable receipt schema implementation;
- signed attestation envelope;
- release capsule verifier;
- comparison with direct SLSA/in-toto adoption.

### Standing

**DESIGN SPECIFICATION / OPEN IMPLEMENTATION.**

## 15. Evidence ledger

| Claim | Strongest current evidence | Current limit |
|---|---|---|
| T1 source singularity | self-hosted mdBook navigation | no longitudinal maintenance comparison |
| T2 deterministic manufacture | real-ggen qualification + replay | independent R4/R5 not established |
| T3 boundary-scoped evidence | split CI/Pages first-run result | productivity advantage not quantified |
| T4 exact-subject law | workflow exact-head assertions | signed receipt binding absent |
| T5 authority separation | PR build vs main deploy split | ecosystem-wide capability graph absent |
| T6 self-hosting | ggen manufacture + mdBook compile | limited external consumer population |
| T7 typed refusal | named refusal/error discipline | MTTR effect unmeasured |
| T8 pack algebra | formal partial-operator specification | not yet mechanized/enforced fully |
| T9 receipt reuse | dependency-closure model | no production receipt cache |
| T10 evidence bottleneck | queueing derivation | repository event study pending |
| T11 coordination collapse | state/edge-count model | organizational field study pending |
| T12 evidence fabric | receipt schema + prior-art mapping | signer/verifier/capsule implementation pending |

## 16. Defense questions

A skeptical committee should ask at least these questions.

### DQ1

Why RDF rather than a typed AST, relational model, or language-specific schema?

**Required answer:** RDF is not axiomatically superior. The thesis depends on graph composability, public vocabulary reuse, queryability, and multi-target semantic leverage. Benchmarks must justify its maintenance cost against alternatives.

### DQ2

Is this merely model-driven engineering with new terminology?

**Required answer:** Many primitives are inherited. Distinction must be demonstrated at the system level: evidence-bounded standing, exact-subject courts, authority separation, distributable pack qualification, self-hosting, and receipt algebra. If literature review shows these are already standard together, novelty claims must narrow.

### DQ3

Does replay prove correctness?

**Required answer:** No. Replay proves a determinism property under an equivalence relation. Independent target compilers, validators, tests, policy, and domain evidence establish other properties.

### DQ4

Who trusts the receipt signer?

**Required answer:** Every receipt system has a trust root. The schema must identify builder/principal and make trust assumptions explicit; signatures do not eliminate compromised builders.

### DQ5

What happens when ontology is wrong?

**Required answer:** Deterministic manufacture reproduces the wrong meaning faithfully. Semantic review, external constraints, tests, domain measurements, and amendment procedures remain necessary.

### DQ6

Can the graph become a monolith?

**Required answer:** Yes. The pack algebra and public-ontology discipline exist partly to prevent universal-schema overcoupling. Domain boundaries and explicit bridges are preferable to one omniscient ontology.

### DQ7

Why not let agents directly perform the workflow?

**Required answer:** Agents may plan and propose. The research hypothesis is that consequential authority benefits from deterministic admission/verification boundaries. This must be compared empirically rather than treated as ideology.

### DQ8

How do you know evidence is the bottleneck?

**Required answer:** We do not yet know universally. The economics chapter states a queueing-derived hypothesis and the experimental chapter defines how to measure it.

### DQ9

Is `ALIVE` just a renamed test pass?

**Required answer:** No. It is claim-scoped closure over exact-subject receipts. A single test can be one premise; it is not automatically the crown.

### DQ10

What would make you abandon the architecture?

**Required answer:** repeated evidence that semantic modeling increases total cost without reducing drift/coordination; composition remains ad hoc; receipts are too expensive/incomplete; deterministic boundaries are routinely bypassed; or external consumers do not generalize from the pack model.

## 17. Minimum evidence for external publication

Before presenting the work as a mature scientific result rather than an engineering research program, the following evidence should exist:

1. a stratified corpus of real packs and consumers;
2. an external-consumer study;
3. R3 or higher reproducibility data;
4. a negative-control suite with measured detection precision;
5. a receipt/standing prototype;
6. one incremental-evidence reuse experiment;
7. a coordination/maintenance baseline study;
8. an authority-containment adversarial study;
9. a completed academic literature review in MDE, build systems, capability security, process mining, and program synthesis;
10. independent replication by a party that did not implement the original pack.

Until then, the strongest description is **an executable research architecture with substantial self-hosting evidence and explicit open proof obligations**.

## 18. Defense criterion

The monograph succeeds if a skeptical reader can disagree with the thesis **precisely**.

They should be able to point to:

- a definition that is too weak;
- a theorem assumption that does not hold;
- a validator that is unsound or vacuous;
- a receipt edge that is missing;
- a benchmark whose baseline is unfair;
- a metric whose denominator is wrong;
- a pack composition that violates the proposed algebra;
- an authority escape;
- a real consumer that falsifies genericity;
- an economic result showing semantic manufacture costs more than it removes.

A theory that admits those attacks can improve. A theory that can only be praised cannot.

## 19. Final defense statement

The work does not ask the reader to believe that software generation is new. It asks a narrower and harder question:

> **Can software construction be reorganized around admitted semantic source, deterministic manufacture, exact evidence, and explicitly bounded authority strongly enough that artifacts cease to be the primary coordination unit?**

The repository, pack algebra, self-hosted book, qualification courts, receipt proposal, and benchmark plan together form a machine-testable attempt to answer that question.
