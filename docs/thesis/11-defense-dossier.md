# Defense dossier: claims, evidence, falsifiers, and proof debt

## 1. Purpose

A dissertation defense should not require a reader to reconstruct the thesis from hundreds of pages. This chapter is the **claim ledger** for the monograph. Every major claim is reduced to:

- the proposition being defended;
- the mechanism that could make it true;
- evidence currently admissible;
- the strongest known falsifier;
- remaining proof/experiment debt.

The dossier intentionally includes incomplete claims. A research system earns credibility by exposing what is not yet proved.

## 2. Claim classes

Claims are classified as:

- **constitutional** — rules the system chooses to enforce;
- **formal** — statements derived from definitions under assumptions;
- **implementation** — statements about repository/runtime behavior;
- **empirical** — statements requiring measurement across episodes/populations;
- **economic** — statements about cost, throughput, coordination, or labor distribution;
- **security** — statements about capability, integrity, or adversarial behavior.

A constitutional rule can be valid policy without being a scientific discovery. Implementation conformance does not prove the rule economically optimal. These categories remain separate.

## 3. Thesis T1 — semantic source singularity

### Claim

For classes of multi-representation software change, one admitted semantic authority plus deterministic projections reduces synchronization state and can reduce human coordination compared with independently maintained representations.

### Mechanism

```text
semantic fact → deterministic projections
```

replaces pairwise synchronization among independently editable representations.

### Evidence

The mdBook self-hosting path models navigation in `docs/book.ttl` and projects `docs/SUMMARY.md`/`book.toml` rather than maintaining them independently. Marketplace catalog/version/config docs similarly prefer executable source over copied volatile values.

### Falsifier

Longitudinal studies show semantic source creates equal or greater maintenance/coordination cost, or generated artifacts require independent edits often enough that source singularity is nominal only.

### Debt

Longitudinal maintenance baseline, drift-incident dataset, authoritative-edit count, reviewer/handoff graph.

### Standing

**PARTIAL_ALIVE as empirical thesis; ALIVE for exercised source-singularity mechanisms at their bounded subjects.**

## 4. Thesis T2 — deterministic semantic manufacture

### Claim

For an exact complete subject, ontology/query/template manufacture can behave as a deterministic compiler projection whose consequences converge under replay.

### Mechanism

`S = (I,G,Q,T,V,E)` and `A = μ(S)`.

### Evidence

Marketplace all-pack qualification exercises real ggen manufacture/replay for admitted subjects; catalog/archive and `pack-maturity-pack` courts compare deterministic consequences.

### Falsifier

An exact subject under its declared environment produces non-equivalent specified consequences on replay.

### Debt

Independent R3–R5 reproduction, hidden-input perturbation, canonical graph/digest semantics for semantic equivalence.

### Standing

**ALIVE for exact subjects/boundaries whose replay courts succeed; UNKNOWN beyond observed replay classes.**

## 5. Thesis T3 — evidence must be boundary-scoped

### Claim

Truth is represented more accurately when success/failure evidence attaches to exact boundaries rather than one repository-level green/red scalar.

### Mechanism

Receipt DAG + claim-specific standing `σ(claim, receipts, time)`.

### Evidence

Marketplace history includes cases where lower/subsystem courts succeeded while a separate aggregate or self-hosting boundary failed. The operating doctrine preserves those facts rather than erasing one with the other.

### Falsifier

Boundary-scoped evidence repeatedly causes worse diagnosis/decision-making than ordinary CI or proves too complex to operate.

### Debt

Executable receipt DAG, standing derivation engine, MTTR/decision-quality study.

### Standing

**ALIVE as demonstrated failure-localization mechanism; productivity advantage remains EMPIRICAL/OPEN.**

## 6. Thesis T4 — exact-subject law

### Claim

Evidence is admissible for a software subject only when the executed immutable source identity equals the claimed identity or claim-complete equivalence is proved.

### Mechanism

Exact checkout + identity assertion + receipt binding.

### Evidence

Crown-bearing marketplace workflows assert exact subject identity; branch/prior-head success is not treated as current evidence after source changes.

### Falsifier

A workflow validates a different immutable tree while satisfying the exact-subject guard, or receipts omit identities needed to distinguish relevant subjects.

### Debt

Tree binding where useful, signed/content-addressed receipts, deliberate mismatch negative controls.

### Standing

**ALIVE for current exact-head assertion behavior where executed; stronger signed binding OPEN.**

## 7. Thesis T5 — SELECT/CONSTRUCT/DO separation

### Claim

Separating reversible construction from consequential actuation permits aggressive candidate generation without granting construction ambient production authority.

### Mechanism

`SELECT → CONSTRUCT → VERIFY → DO` with phase-specific capabilities.

### Evidence

Pull-request documentation/self-hosting can construct/build without receiving main-only Pages deployment authority; marketplace qualification manufactures artifacts but does not execute generated Terraform, MCP calls, cloud mutations, or arbitrary external actuators.

### Falsifier

Construction contexts can directly perform consequential mutation through available capabilities, or real workflows routinely require broad authority that defeats the separation.

### Debt

Capability graph, policy verifier, confused-deputy/adversarial tests, secret/remote-write absence receipts.

### Standing

**ALIVE for bounded demonstrated workflow separations; ecosystem-wide claim PARTIAL_ALIVE.**

## 8. Thesis T6 — self-hosting is stronger integration evidence

### Claim

A marketplace-critical pack manufacturing real marketplace infrastructure provides stronger integration evidence than a synthetic fixture alone.

### Mechanism

The marketplace distributes `P` and infrastructure consumes `P`.

### Evidence

The mdBook pattern-language pack manufactures the marketplace's own book control surface, then mdBook independently compiles the result.

### Falsifier

Self-hosting becomes so implementation-coupled that it stops detecting defects or predicts external-consumer compatibility poorly.

### Debt

External-consumer population, defect-discovery comparison, anti-backdoor controls.

### Standing

**ALIVE for exact self-hosting build subjects that execute successfully; predictive superiority EMPIRICAL/OPEN.**

## 9. Thesis T7 — typed refusal improves repairability

### Claim

Typed localizable refusal reduces diagnostic entropy and may reduce repair lead time relative to generic failure.

### Mechanism

`REFUSED:<domain>:<predicate>` partitions failure space.

### Evidence

Marketplace admission/qualification, `L5-DOC-*`, and authority/identity courts use typed refusal families instead of silently skipping invalid states.

### Falsifier

Codes are routinely wrong/stale or fail to reduce repair time enough to justify maintenance cost.

### Debt

Seeded-failure experiment, MTTR comparison, refusal precision/confusion matrix.

### Standing

**DERIVED for information partitioning; empirical MTTR claim UNKNOWN.**

## 10. Thesis T8 — pack composition can become algebraic

### Claim

A useful subset of packs can compose under a partial operator with explicit graph, target, dependency, toolchain, evidence, and authority compatibility predicates.

### Mechanism

`⊗ : Pack × Pack ⇀ Pack`.

### Evidence

The pack-algebra chapter defines target ownership, conditional associativity, refinement, supersession, authority joins, evidence invalidation, and cross-pack gates. Operational class/consolidation docs now apply the model to real pack families.

### Falsifier

Real interactions require ad-hoc global side effects so frequently that compatibility predicates cannot remain compositional.

### Debt

Machine-readable target ownership, typed dependency edges, authority join policy, cross-pack fixtures, mechanized pure subset.

### Standing

**FORMAL DESIGN / MECHANIZATION CANDIDATE; implementation PARTIAL_ALIVE.**

## 11. Thesis T9 — incremental evidence reuse can safely reduce validation cost

### Claim

If proof dependencies are complete and exact claim-relevant identities are unchanged/equivalent, receipts outside changed dependency closure can be reused.

### Mechanism

`invalidate(Δ) = Reachable_R(Δ)`.

### Falsifier

A reused receipt is later invalidated by an unmodeled dependency, or dependency tracking costs exceed re-execution savings.

### Debt

Complete dependency extraction, equivalence policy, stale-receipt controls, false-reuse monitoring.

### Standing

**OPEN implementation hypothesis.**

## 12. Thesis T10 — evidence becomes the bottleneck after construction collapses

### Claim

When manufacturing throughput rises materially faster than validation/actuation throughput, evidence WIP dominates delivery lead time.

### Mechanism

Little's Law applied separately to manufacture, evidence, and actuation queues.

### Falsifier

Measured high-automation repositories remain construction-limited, or evidence scales automatically enough that no persistent queue forms.

### Debt

Longitudinal event log, queue classification, observed rates/WIP/lead time, before/after deterministic-pack coverage.

### Standing

**THEORETICALLY MOTIVATED, EMPIRICALLY OPEN.**

## 13. Thesis T11 — coordination can collapse from clique to star

### Claim

When many representations share one semantic authority, synchronization relationships can become star-shaped projections instead of independent pairwise coordination.

### Mechanism

Independent model: `E_sync ≈ n(n-1)/2`; projection model: `E_projection ≈ n`.

### Falsifier

Adapters/ontology governance recreate equivalent pairwise coordination, or the semantic source becomes a universal bottleneck.

### Debt

Empirical handoff graph, representation-change study, ontology-governance cost.

### Standing

**DERIVED as structural model; organizational claim OPEN.**

## 14. Thesis T12 — receipts can become a content-addressed evidence fabric

### Claim

Structured receipts bound to immutable identities can support standing derivation, provenance audit, incremental invalidation, Level-5 closure, and release reconstruction more reliably than ephemeral badges/logs alone.

### Mechanism

Receipt DAG + content identity + policy-versioned standing derivation.

### Prior-art alignment

PROV-O, in-toto, SLSA provenance, Git identity, and reproducible-build practice provide foundations. Marketplace-specific work integrates semantic manufacture, typed boundary standing, class closure, Diátaxis correspondence, and actuation authority.

### Falsifier

Receipt capture is too incomplete/expensive to derive useful standing or merely duplicates existing attestation systems without additional operational value.

### Debt

Interoperable receipt implementation, signed envelope, release capsule verifier, comparison with direct SLSA/in-toto adoption.

### Standing

**DESIGN SPECIFICATION / OPEN IMPLEMENTATION.**

## 15. Thesis T13 — Level 5 is class/evidence closure, not artifact polish

### Claim

For a reusable pack family, the strongest maturity state is reached only when seven claim-relevant dimensions close over the exact subject—semantic source, admission, manufacture, execution, receipt/replay, authority fence, and composition/class closure—while Tutorial/How-to/Reference/Explanation correspond to that same contract.

### Mechanism

Maturity vector:

`M(P,S) = (m_s,m_a,m_m,m_e,m_r,m_ω,m_c)`

with non-compensatory evidence closure, plus:

`L5Doc = Tutorial ∧ HowTo ∧ Reference ∧ Explanation ∧ Corr_D ∧ Exec_D`.

Class closure factors repeated authority into kernels/capabilities while preserving domain/world/runtime/compatibility differences and preventing authority widening.

### Current implementation evidence

- `pack-maturity-pack` manufactures reusable fixed-point/receipt/Diátaxis mechanics and typed `L5-DOC-*` structural refusals;
- marketplace reference/how-to/tutorial/explanation now defines the 5×7 contract and class-closure procedure;
- the new Level-5 thesis chapter formalizes non-compensation, class taxonomy, consolidation morphisms, authority non-expansion, and falsifiers;
- mdBook navigation remains generated from semantic source, demonstrating documentation source singularity.

### Falsifier

The model should narrow or be abandoned if class factoring increases total coordination cost, shared kernels become unstable mega-ontologies, structural Diátaxis systematically produces misleading docs, authority widens under umbrellas, domain teams must routinely fork canonical classes, or exact evidence closure costs more than the defects it prevents.

### Debt

- machine-readable pack class/supersession/target-ownership graph;
- automated consolidation diagnostics/court;
- consumer migration graph/witnesses;
- machine standing lattice over all seven dimensions;
- source-to-doc executable correspondence beyond structural `L5-DOC-*` checks;
- portfolio before/after measurement of duplicated authority, drift, change lead time, and consumer migration cost.

### Standing

**Level-5 Diátaxis structure: EXECUTABLE for the generic structural boundary; 5×7/class taxonomy: operational specification; class-closure automation and portfolio benefit: OPEN/PARTIAL_ALIVE. No global L5 crown is implied for the corpus.**

## 16. Evidence ledger

| Claim | Strongest current evidence | Current limit |
|---|---|---|
| T1 source singularity | self-hosted semantic mdBook navigation/catalog/config law | no longitudinal maintenance comparison |
| T2 deterministic manufacture | real-ggen qualification + replay | independent R4/R5 not established |
| T3 boundary-scoped evidence | exact-subject court separation | productivity advantage unquantified |
| T4 exact-subject law | workflow identity assertions | signed receipt binding incomplete |
| T5 authority separation | construction/build vs main deploy boundaries | ecosystem capability graph incomplete |
| T6 self-hosting | ggen manufacture + mdBook target compile | limited external-consumer population |
| T7 typed refusal | repository/ggen/L5-DOC refusal discipline | MTTR effect unmeasured |
| T8 pack algebra | partial-operator formal specification | mechanization incomplete |
| T9 receipt reuse | dependency-closure model | no production proof cache |
| T10 evidence bottleneck | queueing derivation | longitudinal event study pending |
| T11 coordination collapse | state/edge-count model | organizational field study pending |
| T12 evidence fabric | receipt schema + prior-art mapping | signer/verifier/capsule implementation pending |
| T13 Level-5 class/evidence closure | 5×7 contract + Diátaxis generator + class/consolidation calculus | portfolio class graph/automated closure court incomplete |

## 17. Defense questions

### DQ1 — Why RDF rather than a typed AST/relational model?

RDF is not axiomatically superior. The thesis depends on graph composability, public-vocabulary reuse, queryability, and multi-target semantic leverage. Benchmarks must justify its cost against alternatives.

### DQ2 — Is this model-driven engineering with new terminology?

Many primitives are inherited. Distinction must be demonstrated at the system level: exact evidence/standing, authority separation, distributable pack qualification, self-hosting, partial pack algebra, class closure, and receipt composition. Novelty claims narrow if literature shows this bundle already standard.

### DQ3 — Does replay prove correctness?

No. Replay proves a declared equivalence property for a subject. Independent compilers, validators, tests, formal checks, policy, and domain evidence prove other predicates.

### DQ4 — Who trusts the receipt signer?

Every receipt system has a trust root. Builder/principal identity and trust assumptions must be explicit; signatures do not rescue compromised builders or incomplete claims.

### DQ5 — What happens when ontology is wrong?

Deterministic manufacture reproduces wrong meaning faithfully. Semantic review, constraints, tests, measurements, negative witnesses, and amendment remain necessary.

### DQ6 — Can the graph/kernel become a monolith?

Yes. Class closure is not “one ontology for everything.” Canonicalize only proved shared law; keep domain/world/runtime boundaries and explicit bridges. Mega-ontology pressure is a falsifier.

### DQ7 — Why not let agents directly perform the workflow?

Agents may observe, plan, select, and construct. Consequential authority benefits from admitted deterministic boundaries and receipts. This is a security/operational hypothesis to test, not ideology.

### DQ8 — How do you know evidence is the bottleneck?

We do not know universally. The economics chapter states a queueing-derived hypothesis and a measurement program.

### DQ9 — Is `ALIVE` just renamed test pass?

No. A test is one receipt/premise. ALIVE is claim-scoped exact-subject evidence closure.

### DQ10 — Why not average the 5×7 maturity matrix?

Because required predicates are conjunctive and non-compensatory. An L5 documentation surface cannot compensate for missing external execution or an unsafe authority join. Averages hide the exact work still required.

### DQ11 — Why consolidate packs at all?

Only when multiple packs duplicate semantic authority. Directory count is not the target. The target is reducing duplicate truth while preserving independent domains/runtimes/compatibility. Consolidation itself must prove benefit and non-escalation.

### DQ12 — What would make you abandon the architecture?

Repeated evidence that semantic modeling increases total cost without reducing drift/coordination; composition remains ad hoc; receipts are too expensive/incomplete; deterministic boundaries are routinely bypassed; class kernels become bottlenecks; external consumers do not generalize; or Level-5 closure becomes ceremony without predictive value.

## 18. Minimum evidence for external publication

Before presenting the work as a mature scientific result rather than an engineering research program, the following should exist:

1. stratified corpus of real packs and consumers;
2. external-consumer study;
3. R3+ reproducibility data;
4. negative-control suite with measured detection precision;
5. receipt/standing prototype;
6. incremental-evidence reuse experiment;
7. coordination/maintenance baseline study;
8. authority-containment adversarial study;
9. machine-readable pack class/target/consumer graph and consolidation court;
10. Level-5 source-to-doc correspondence experiment beyond structural completeness;
11. completed academic literature review across MDE, build systems, capability security, process mining, program synthesis, documentation engineering, and software-product-line/modularity work;
12. independent replication by a party that did not implement the original pack.

Until then, the strongest description remains **an executable research architecture with substantial self-hosting evidence and explicit open proof obligations**.

## 19. Defense criterion

The monograph succeeds if a skeptical reader can disagree with it precisely by pointing to a weak definition, invalid theorem assumption, unsound/vacuous validator, missing receipt edge, unfair benchmark, wrong denominator, non-compositional pack interaction, authority escape, misleading maturity coordinate, unsafe consolidation, external consumer falsifier, or economic result showing semantic manufacture/class closure costs more than it removes.

A theory that admits those attacks can improve. A theory that can only be praised cannot.

## 20. Final defense statement

The work does not ask the reader to believe that software generation is new. It asks a narrower and harder question:

> **Can software construction and reuse be reorganized around admitted semantic source, deterministic manufacture, exact evidence, explicit class composition, documentation correspondence, and bounded authority strongly enough that artifacts cease to be the primary coordination unit?**

The repository, Level-5 contract, pack algebra, class-closure model, self-hosted book, qualification courts, receipt proposal, and benchmark program together form a machine-testable attempt to answer that question.
