# Theorem catalogue and proof obligations

## 1. Purpose

The monograph defines architecture, invariants, Level-5 maturity, Diátaxis correspondence, and class closure. This chapter turns those ideas into a **proof catalogue**: definitions, lemmas, propositions, counterexamples, and explicit proof status.

Every result carries one of these statuses:

- **DERIVED** — follows from stated definitions under named assumptions;
- **EXECUTABLE** — enforced or falsified by repository/runtime checks for exercised subjects;
- **EMPIRICAL** — supported only by finite observed runs;
- **MECHANIZATION CANDIDATE** — precise enough for a proof assistant/declarative constraint system, but not yet mechanically proved;
- **OPEN** — plausible research claim with unresolved proof obligations.

A theorem about a model does not establish implementation conformance. An executable test does not establish a universal theorem. The useful system binds the two through exact identities and receipts.

## 2. Core definitions

### Definition 2.1 — Observation

An **observation** `O` is information available before admission. Observation alone grants no manufacturing or actuation authority.

### Definition 2.2 — Admission

An admission function is partial:

`α : O ⇀ O*`

where `O*` is the observation permitted to influence the next bounded transition. Undefined `α(O)` is a refusal/unsupported condition, not implicit success.

### Definition 2.3 — Manufacturing subject

`S = (I, G, Q, T, V, E)`

where `I` is identity/provenance, `G` admitted semantic source, `Q` selection/query program, `T` projection/template program, `V` manufacturing toolchain identity, and `E` declared relevant environment.

A subject is exact only when each claim-relevant component used by execution is bound to the claimed identity.

### Definition 2.4 — Lawful manufacture

`μ : S ⇀ A`

maps an admitted subject to a finite artifact set. Manufacture is lawful only when execution stays within declared authority/mutation bounds.

### Definition 2.5 — Replay equivalence

Given artifact equivalence `≈`, manufacture is replay-equivalent for `S` when independent executions preserving relevant inputs produce equivalent consequences. For byte-reproducibility, `≈` is byte identity; other domains MUST define their relation before claiming replay.

### Definition 2.6 — Consequential actuation

`DO` is a transition whose externally visible consequences cannot be treated as ordinary reversible construction in the bounded workspace: publication, merge, send, remote infrastructure mutation, access-control change, production API invocation, and similar effects.

### Definition 2.7 — Receipt

A receipt binds:

`(subject, claim, boundary, executor, toolchain, inputs, outputs, result, authority, time, parents)`.

### Definition 2.8 — Standing

`σ : (claim, receipts, now) → {UNKNOWN, PARTIAL_ALIVE, ALIVE, BLOCKED, BUILD_BROKEN, UNSUPPORTED, REFUSED:*}`.

Standing is claim-scoped and time/evidence-epoch scoped. There is no architecture-wide scalar green.

### Definition 2.9 — Exact-head execution

An execution is exact-head when the source tree actually executed equals the immutable tree identified by the claimed subject commit (or a claim-complete equivalence proof exists).

### Definition 2.10 — Independent boundary

Validation boundaries `b1` and `b2` are independent for failure propagation when failure of `b2` does not negate predicates established by `b1` for the same immutable subject. Independence is proved/justified, never assumed from job names.

### Definition 2.11 — Maturity vector

For pack `P` and exact subject `S`:

`M(P,S) = (m_s, m_a, m_m, m_e, m_r, m_ω, m_c)`

representing semantic source, admission, manufacture, execution, receipt/replay, authority fence, and composition/class closure. Each coordinate ranges over `L1 < L2 < L3 < L4 < L5`.

### Definition 2.12 — Diátaxis closure

`D(P,S) = (T_u, H, R_f, E_x)` where Tutorial, How-to, Reference, and Explanation remain distinct projections of one admitted contract.

Structural closure:

`D_4 = T_u ∧ H ∧ R_f ∧ E_x`.

Strong documentation standing additionally requires correspondence and execution of documented paths:

`L5Doc = D_4 ∧ Corr_D ∧ Exec_D`.

### Definition 2.13 — Class closure

For pack family `F`, class closure is the factoring state in which repeated equivalent semantic/protocol/lifecycle/projection authority is canonicalized into explicit kernels/capabilities while non-equivalent domain/world/runtime/compatibility differences remain explicit and authority does not widen accidentally.

## 3. Determinism results

### Theorem 3.1 — Fixed-subject functional determinism

If `μ` is a mathematical function over a complete subject `S`, all evaluations of `μ(S)` are equal.

**Status:** DERIVED.

An observed nondeterministic replay therefore indicates at least one of: impure implementation, incomplete subject/environment, or underspecified artifact equivalence.

### Proposition 3.2 — Stable selection is necessary for stable ordered projection

If artifact semantics preserve query row order, unconstrained selection order cannot establish ordered projection determinism.

**Status:** DERIVED + EXECUTABLE CANDIDATE.

SPARQL ordering must therefore be explicit (e.g. `ORDER BY`) or normalized by an equivalent deterministic step when row order matters.

### Proposition 3.3 — Repeated success is weaker than independent reproducibility

Two successful runs in one preserved environment establish replay evidence but not third-party reproducibility from a release capsule.

**Status:** DERIVED.

## 4. Subject identity results

### Theorem 4.1 — Exact-subject necessity

A receipt from immutable subject `S1` is insufficient for a claim about distinct immutable subject `S2` unless an admissible equivalence proof covers every claim-relevant difference.

**Status:** DERIVED; exact-head assertions are EXECUTABLE.

**Corollary:** “the branch passed earlier” cannot crown the current head.

**Corollary:** documentation-looking changes are not automatically irrelevant; irrelevance itself is a dependency/equivalence claim.

### Proposition 4.2 — Tree identity is stronger than branch-name identity

A mutable branch ref alone cannot provide durable source identity.

**Status:** DERIVED.

## 5. Authority results

### Theorem 5.1 — Capability exclusion implies direct non-actuation

If constructor `C` has no reachable capability for consequential boundary `D`, `C` cannot directly perform `D` through that excluded capability.

**Status:** DERIVED; implementation conformance is EXECUTABLE/SECURITY TESTABLE.

This is not a global security theorem: confused-deputy paths and unintended capabilities remain possible.

### Theorem 5.2 — Construction/actuation separation preserves optionality

If a candidate can be constructed without actuation, rejecting it after construction does not require reversing the external consequence that actuation would have caused.

**Status:** DERIVED.

### Proposition 5.3 — Authority monotonicity is unsafe by default

Composing two packs/workflows by unconstrained union of capabilities can introduce effective authority neither required alone.

**Status:** DERIVED.

Therefore authority composition is a policy-governed partial join, not set union.

## 6. Evidence results

### Theorem 6.1 — Local failure preservation

If receipt `r1` establishes `P1(S)` at boundary `b1` and later independent boundary `b2` fails while evaluating `P2(S)`, the `b2` failure does not invalidate `r1` when `P1` has no premise requiring `P2`.

**Status:** DERIVED; marketplace self-hosting provides an EMPIRICAL instance.

### Theorem 6.2 — Broader claims require evidence closure

If claim `C` requires predicates `{P1,…,Pn}`, `ALIVE(C)` is sound only when admissible receipts establish all required predicates for equivalent exact subjects and compatible evidence epochs.

**Status:** DERIVED; MECHANIZATION CANDIDATE.

### Proposition 6.3 — Standing is not globally monotone in wall-clock time

Historical ALIVE can become non-current when a claim-relevant identity, dependency, policy, environment, or validity epoch changes.

**Status:** DERIVED.

### Proposition 6.4 — Refusal carries more diagnostic information than generic failure

Typed refusal partitions failure space more finely than one undifferentiated error state.

**Status:** DERIVED from information partitioning; MTTR advantage remains EMPIRICAL/OPEN.

## 7. Source-of-truth results

### Proposition 7.1 — Duplicate independent authorities increase possible drift states

If one fact is independently editable in `n` authoritative representations, inconsistent states exist that disappear when one representation is canonical and the rest are deterministic projections.

**Status:** DERIVED under the independent-edit model.

This does not prove RDF is always the correct authority. It proves duplicated authority has a state-space cost.

### Proposition 7.2 — Generated-output reviewability does not require generated-output authority

A generated consequence may be committed/inspected without becoming canonical source if upstream regeneration and drift detection remain authoritative.

**Status:** DERIVED; EXECUTABLE in the mdBook self-hosting pattern.

## 8. Pack composition and class-closure results

### Theorem 8.1 — Conditional associativity of independent pack composition

For packs `P,Q,R`, if semantic unions remain admitted, target merge operators are associative/non-conflicting, identifiers are scoped, dependencies normalize equivalently, cross-gates represent the same predicates, and authority joins are associative under policy, then:

`(P ⊗ Q) ⊗ R ≡ P ⊗ (Q ⊗ R)`.

**Status:** DERIVED CONDITIONALLY; MECHANIZATION CANDIDATE.

### Proposition 8.2 — Pack composition is not generally commutative

`P ⊗ Q ≠ Q ⊗ P` when ordering, overwrite policy, dependency direction, cross-gate semantics, supersession, or authority is significant.

**Status:** DERIVED.

### Proposition 8.3 — Semantic graph union is idempotent; manufacture need not be

For RDF graphs as triple sets, `G ∪ G = G`, but applying a pack twice may still fail fixed-point behavior if projection observes timestamps, mutable filesystem state, counters, randomness, or other unmodeled input.

**Status:** DERIVED.

### Theorem 8.4 — Maturity dimensions are non-compensatory for conjunctive claims

Let `C_L5` require predicates over the seven maturity dimensions. If any required predicate is unestablished, stronger evidence on other independent dimensions cannot establish `C_L5`.

**Status:** DERIVED; executable standing derivation remains MECHANIZATION CANDIDATE.

**Proof.** `C_L5` is defined by evidence closure over required predicates. A conjunction with a missing premise is not proved by additional evidence for another premise. ∎

### Proposition 8.5 — Structural Diátaxis closure is weaker than documentation correspondence

The existence of non-empty Tutorial, How-to, Reference, and Explanation documents does not imply that their commands, source facts, generated surfaces, refusals, authority boundaries, and replay claims correspond to the exact implementation subject.

**Status:** DERIVED; structural `L5-DOC-*` court is EXECUTABLE for its claimed subset.

### Proposition 8.6 — Class closure can reduce duplicated semantic authority without reducing pack-instance diversity

If duplicated family facts are moved to one canonical kernel and profile/world-specific facts remain parameterized, the number of independent semantic owners can decrease while the number of usable pack instances stays constant or grows.

**Status:** DERIVED under the factoring model; portfolio cost/benefit is EMPIRICAL/OPEN.

### Theorem 8.7 — Authority-preserving consolidation is non-expansive

If consolidation claims semantic/consumer preservation and introduces no new authority contract, any successor capability permitting a new consequential transition falsifies the preservation claim.

**Status:** DERIVED; policy mechanization OPEN.

### Proposition 8.8 — Supersession requires consumer evidence

The existence of successor pack `P'` is insufficient to prove safe replacement of `P`. Supersession requires a migration witness over affected consumer classes or an explicit incompatible subset.

**Status:** DERIVED; consumer-graph automation OPEN.

## 9. Security propositions

### Proposition 9.1 — Provenance without authority evidence is incomplete for actuation claims

Knowing which inputs produced an artifact does not prove the actor performing an external mutation was authorized.

**Status:** DERIVED.

### Proposition 9.2 — Authority without provenance is incomplete for artifact-integrity claims

An authorized deployer may deploy the wrong subject. Consequential standing therefore requires identity/provenance and authority evidence.

**Status:** DERIVED.

### Proposition 9.3 — Hash identity is conditional on canonical bytes and named algorithm

A digest claim is meaningless without algorithm and representation/canonicalization domain. Semantically equivalent RDF serializations need not have identical bytes.

**Status:** DERIVED.

## 10. Proof-obligation matrix

| ID | Property | Current evidence class | Stronger target |
|---|---|---|---|
| PO-01 | exact subject executed | workflow assertion | signed receipt bound to commit/tree |
| PO-02 | pack source non-mutation | qualification filesystem comparison | independent verifier + receipt digest |
| PO-03 | replay convergence | repeated real-ggen manufacture | cross-runner reproducibility classes |
| PO-04 | navigation position uniqueness | model convention/query order | SHACL shape + negative control |
| PO-05 | chapter path confinement | target compiler/filesystem behavior | explicit path gate + shape/query constraint |
| PO-06 | authority separation | workflow permissions/job split | capability graph + policy verifier |
| PO-07 | evidence closure for standing | procedural interpretation | executable standing derivation over receipt DAG |
| PO-08 | pack composition associativity | conditional model | mechanized algebra for admitted subset |
| PO-09 | receipt integrity | CI logs/metadata | signed/transparency-bound receipt capsule |
| PO-10 | independent reproducibility | same-platform replay | independently reconstructed release capsule |
| PO-11 | Level-5 vector non-compensation | normative/reference model | machine standing lattice over seven dimensions |
| PO-12 | Diátaxis correspondence | generated structural L5-DOC court | source/command/refusal/authority execution bindings |
| PO-13 | class closure | documented taxonomy/procedure | RDF class/target/consumer graph + typed consolidation court |
| PO-14 | consolidation authority non-escalation | policy/review doctrine | machine capability-before/after proof + negative controls |
| PO-15 | safe supersession | manual migration evidence | consumer graph + executable migration witness |

## 11. Countermodel discipline

For every theorem-shaped statement, maintain a countermodel/failing fixture where feasible.

Examples:

- omit `ORDER BY` to challenge ordered determinism;
- change the checked-out SHA to challenge exact-head law;
- introduce duplicate navigation positions to challenge totality;
- add a timestamp to a template to challenge replay convergence;
- grant qualification a deployment capability to challenge authority separation;
- hand-edit a generated consequence to challenge source singularity;
- mutate pack source during qualification to challenge non-mutation;
- reuse a receipt after toolchain change to challenge evidence equivalence;
- remove one Diátaxis quadrant to challenge structural Level-5 docs closure;
- keep four docs but stale a reference command to challenge correspondence;
- compose two profiles that own the same target to challenge class closure;
- give an umbrella a new remote-write capability to challenge authority-preserving consolidation;
- delete a legacy pack with an unmigrated consumer to challenge supersession law.

A countermodel suite is stronger than a principles list because it proves validators can observe representative violations.

## 12. Mechanization roadmap

### M1 — Graph constraints

Use SHACL or equivalent declarative constraints for local graph properties: cardinality, allowed kinds, path presence, unique positions, namespace/identity, pack class/supersession/target ownership where expressible.

### M2 — Executable transition contracts

Use repository/runtime courts for filesystems, toolchains, process isolation, replay, target compilers, native consumer behavior, Diátaxis command correspondence, authority boundaries, and migration witnesses.

### M3 — Algebraic and temporal proofs

Use a theorem prover for evidence closure, partial-order standing, composition laws, authority non-escalation, class-closure properties, receipt-DAG consistency, and safe incremental proof reuse.

Formal artifacts should consume identities/proof obligations derived from the same admitted source as runtime qualification; a disconnected proof model would create a second authority.

## 13. Research standard

> **Every universal claim resolves to a definition plus proof obligation; every implementation claim resolves to executable exact-subject evidence; every empirical claim resolves to a protocol and dataset; every consolidation resolves to equivalence/migration/authority evidence; and every crown names the exact subject and boundary it crowns.**

This is the point where the monograph becomes more than architecture documentation: its statements can be proved, executed, falsified, narrowed, or retired.
