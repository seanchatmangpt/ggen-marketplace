# Theorem catalogue and proof obligations

## 1. Purpose

The earlier chapters define the architecture and motivate its invariants. This chapter turns those invariants into a **proof catalogue**: definitions, lemmas, propositions, counterexamples, and explicit proof status. The intent is to prevent a common failure mode in systems research where words such as “deterministic,” “safe,” or “reproducible” silently move between mathematical, implementation, and operational meanings.

Every result below therefore carries a status:

- **DERIVED** — follows from stated definitions under named assumptions.
- **EXECUTABLE** — enforced or falsified by repository/runtime checks.
- **EMPIRICAL** — supported only by observed runs over a finite corpus.
- **MECHANIZATION CANDIDATE** — precise enough to encode in a proof assistant or declarative constraint system, but not yet mechanically proved.
- **OPEN** — plausible research claim with unresolved proof obligations.

The catalogue is deliberately conservative. A theorem about a model does not establish that an implementation conforms to the model. An executable test does not establish a universal theorem. The useful system binds the two.

## 2. Core definitions

### Definition 2.1 — Observation

An **observation** `O` is information available to the manufacturing system before admission. It may contain facts, claims, files, graph statements, repository state, configuration, or tool output. Observation alone grants no manufacturing or actuation authority.

### Definition 2.2 — Admission

An **admission function** `α` is a partial function:

`α : O ⇀ O*`

where `O*` is the subset or transformed representation of observation permitted to influence the next bounded transition. Undefined `α(O)` is a refusal or unsupported condition, not an implicit success.

### Definition 2.3 — Manufacturing subject

A **subject** is a tuple:

`S = (I, G, Q, T, V, E)`

where:

- `I` is identity and provenance;
- `G` is admitted semantic source;
- `Q` is the selection/query program;
- `T` is the projection/template program;
- `V` is the manufacturing toolchain identity;
- `E` is the declared relevant environment.

A subject is exact only when each component used by the execution is bound to the claimed identity.

### Definition 2.4 — Lawful manufacture

A manufacturing function `μ` maps an admitted subject to a finite artifact set:

`μ : S ⇀ A`

A manufacture is **lawful** only if the execution stays within the authority and mutation bounds declared by the governing contract.

### Definition 2.5 — Replay equivalence

Given an equivalence relation `≈` over artifacts, manufacture is replay-equivalent for subject `S` when:

`μ(S) ≈ μ(S)`

across independent executions that preserve all declared relevant inputs.

For byte-reproducible artifacts, `≈` is byte identity. For other domains the equivalence relation MUST be explicitly defined before a replay claim is meaningful.

### Definition 2.6 — Consequential actuation

`DO` is any transition whose externally visible consequences cannot be treated as an ordinary reversible construction inside the bounded workspace. Examples include publishing, merging, sending, mutating remote infrastructure, changing access control, or invoking an external production API.

### Definition 2.7 — Receipt

A **receipt** is an evidence object binding:

`(subject, boundary, executor, toolchain, inputs, outputs, result, authority, time)`

plus references to predecessor receipts required to justify the transition.

### Definition 2.8 — Standing

**Standing** is a function over a claim and an evidence set:

`σ : (claim, receipts, now) → {UNKNOWN, PARTIAL_ALIVE, ALIVE, BLOCKED, BUILD_BROKEN, UNSUPPORTED, REFUSED:*}`

Standing is claim-scoped and time-scoped. There is no architecture-wide scalar “green.”

### Definition 2.9 — Exact-head execution

An execution is **exact-head** when the source tree actually executed by a validation boundary is the tree identified by the claimed subject commit.

### Definition 2.10 — Independent boundary

Two validation boundaries `b1` and `b2` are independent with respect to failure propagation when failure of `b2` does not negate the predicates previously established by `b1` for the same immutable subject.

Independence is a relation to be proved or operationally justified, not assumed from different job names.

## 3. Determinism results

### Theorem 3.1 — Fixed-subject functional determinism

**Statement.** If `μ` is a mathematical function over a complete subject `S`, then all evaluations of `μ(S)` are equal.

**Status:** DERIVED.

**Proof.** This is immediate from the definition of a function: one element of the domain maps to at most one element of the codomain. ∎

**Engineering consequence.** An observed nondeterministic replay demonstrates at least one of three defects:

1. the implementation is not functionally deterministic;
2. `S` omitted a relevant environmental input;
3. the chosen artifact equivalence relation is underspecified.

The theorem does not let an implementation declare determinism by definition. It tells us what a replay failure means.

### Proposition 3.2 — Stable selection is necessary for stable ordered projection

**Statement.** If the emitted artifact preserves the iteration order of query result rows and that order is semantically significant, then a query whose result order is unconstrained cannot establish ordered projection determinism.

**Status:** DERIVED + EXECUTABLE CANDIDATE.

**Reasoning.** SPARQL result order is not a semantic total order unless ordering is requested. Therefore a template that depends on row order requires an explicit ordering clause or an equivalent deterministic normalization step.

**Repository instance.** The mdBook navigation query uses `ORDER BY ?position` because chapter sequence is part of the book's semantics.

### Proposition 3.3 — Repeated success is weaker than independent reproducibility

**Statement.** Two successful runs in the same preserved environment establish replay evidence but do not establish that an independent party can reproduce the artifact from the declared source and environment specification.

**Status:** DERIVED.

This distinguishes **replay convergence** from the stronger reproducible-build notion used by the Reproducible Builds project. The experimental chapter defines increasingly independent replay classes.

## 4. Subject identity results

### Theorem 4.1 — Exact-subject necessity

**Statement.** A receipt from execution over subject `S1` is insufficient evidence for a claim about distinct immutable subject `S2` unless an admissible equivalence proof establishes that every claim-relevant input is equivalent.

**Status:** DERIVED; exact-head assertion is EXECUTABLE.

**Proof sketch.** Assume `S1 ≠ S2`. Then at least one component differs. Without proving that the differing component is irrelevant to the claim, there exists a possible manufacturing function for which `μ(S1) ≠ μ(S2)`. Therefore the receipt cannot soundly establish the result for `S2`. ∎

**Corollary 4.1.1.** “The branch passed earlier” is not evidence that the current head passes.

**Corollary 4.1.2.** A merge-base receipt cannot crown a descendant commit merely because the descendant only “looks like documentation.” The irrelevance of the change would itself need proof.

### Proposition 4.2 — Tree identity is stronger than branch-name identity

**Statement.** A mutable branch ref alone cannot provide durable source identity.

**Status:** DERIVED.

A branch name may resolve to different commits at different times. Receipts intended for durable audit therefore bind to immutable commit/tree identities, while a branch remains routing metadata.

## 5. Authority results

### Theorem 5.1 — Capability exclusion implies direct non-actuation

**Statement.** Let constructor `C` execute in an environment with no capability that can invoke consequential boundary `D`. Then `C` cannot directly perform `D` through the excluded capability.

**Status:** DERIVED; implementation conformance is EXECUTABLE/SECURITY TESTABLE.

**Proof.** By assumption the capability required for the direct transition is absent from the constructor's reachable authority set. Therefore that transition is not available to `C` through that capability. ∎

**Important limitation.** This theorem does not prove global security. A constructor might still exploit an unintended capability, confuse a deputy, or manufacture a payload later actuated by another principal. Hence authority analysis is a graph problem, not a boolean “sandboxed” label.

### Theorem 5.2 — Construction/actuation separation preserves optionality

**Statement.** If a candidate artifact can be constructed without performing its consequential actuation, then rejecting that candidate after construction does not require reversing the external consequence that actuation would have caused.

**Status:** DERIVED.

This is the formal reason to maximize reversible construction before `DO`. It increases the search space available to the planner while minimizing rollback obligations.

### Proposition 5.3 — Authority monotonicity is unsafe by default

**Statement.** Composing two packs or workflows by unioning their authorities can introduce capabilities that neither component required in isolation.

**Status:** DERIVED.

Therefore pack composition MUST NOT define authority as unconstrained set union. The pack-algebra chapter defines an authority join only under explicit policy.

## 6. Evidence results

### Theorem 6.1 — Local failure preservation

**Statement.** Suppose receipt `r1` establishes predicate `P1(S)` at boundary `b1`, and a later independent boundary `b2` fails while evaluating predicate `P2(S)`. If `P1` does not logically depend on success of `b2`, the `b2` failure does not invalidate `r1`.

**Status:** DERIVED; self-hosting run provides EMPIRICAL instance.

**Proof.** The truth of `P1(S)` was established by `r1`. By boundary independence, `P1` has no premise requiring `P2`. Therefore failure to establish `P2` does not negate `P1`. ∎

This is the reason the first mdBook Pages failure did not erase the already-successful generic pack qualification.

### Theorem 6.2 — Broader claims require evidence closure

**Statement.** Let claim `C` require predicates `{P1, …, Pn}`. `ALIVE(C)` is sound only when admissible receipts establish all required predicates for equivalent subjects and compatible evidence epochs.

**Status:** DERIVED; MECHANIZATION CANDIDATE.

The evidence graph therefore behaves like a proof DAG: a crown is the closure of required premises, not the presence of one distinguished green check.

### Proposition 6.3 — Standing is not globally monotone in wall-clock time

**Statement.** An `ALIVE` standing can become `UNKNOWN` or otherwise non-current when an identity, dependency, policy, credential, environment, or validity epoch changes.

**Status:** DERIVED.

A durable historical receipt remains true as an observation about its execution, but its applicability to a current claim may expire.

### Proposition 6.4 — Refusal carries more information than generic failure

**Statement.** For diagnosis, a typed refusal partitions the failure space more finely than a single undifferentiated error state.

**Status:** DERIVED from information partitioning; empirical productivity effect remains OPEN.

The empirical hypothesis is that finer partitioning lowers mean repair time. That must be measured rather than assumed.

## 7. Source-of-truth results

### Proposition 7.1 — Duplicate independent authorities increase possible drift states

**Statement.** If one semantic fact is independently editable in `n` authoritative representations, the system admits inconsistent states that do not exist when that fact has one authority and `n-1` deterministic projections.

**Status:** DERIVED under the independent-edit model.

For a binary fact duplicated twice, the synchronized model permits two consistent assignments while independent duplicated authority permits four assignments, two of them inconsistent. The combinatorial gap grows with fact cardinality and representation count.

This does not prove RDF should be the authority for every fact. It proves that **duplicating authority has a state-space cost**.

### Proposition 7.2 — Generated output reviewability does not require generated output authority

**Statement.** A generated consequence may be committed for inspection without becoming canonical source if regeneration and drift detection remain defined by upstream source.

**Status:** DERIVED; EXECUTABLE in the mdBook pattern.

This permits `book.toml` and `SUMMARY.md` to be reviewable artifacts while `docs/book.ttl` and templates retain semantic authority.

## 8. Pack composition results

The next chapter gives a formal algebra. The most important results are summarized here.

### Theorem 8.1 — Conditional associativity of independent pack composition

**Statement.** For packs `P`, `Q`, and `R`, if their semantic unions are consistent, their target namespaces are non-conflicting, their query/template identifiers are scoped, and their authority composition is associative under the governing policy, then:

`(P ⊗ Q) ⊗ R ≡ P ⊗ (Q ⊗ R)`

with respect to the declared artifact equivalence relation.

**Status:** DERIVED CONDITIONALLY; MECHANIZATION CANDIDATE.

### Proposition 8.2 — Pack composition is not generally commutative

`P ⊗ Q ≠ Q ⊗ P`

when ordering, overwrite policy, dependency direction, gate sequencing, or authority inheritance is significant.

**Status:** DERIVED.

Any implementation that assumes commutativity MUST prove the independence conditions for the relevant pair.

### Proposition 8.3 — Semantic graph union is idempotent; manufacture need not be

For RDF graphs treated as sets of triples:

`G ∪ G = G`.

But applying a pack twice can still fail idempotence if templates depend on mutable filesystem state, timestamps, counters, or other unmodeled inputs.

**Status:** DERIVED.

This distinction is a useful diagnostic: semantic idempotence does not rescue an impure projection.

## 9. Security propositions

### Proposition 9.1 — Provenance without authority evidence is incomplete for actuation claims

**Statement.** Knowing which inputs produced an artifact does not alone prove that the actor that published or mutated an external system was authorized to do so.

**Status:** DERIVED.

Supply-chain provenance and actuation authority are complementary evidence dimensions.

### Proposition 9.2 — Authority without provenance is incomplete for artifact integrity claims

The inverse also holds: an authorized deployer may deploy the wrong subject. Therefore consequential standing requires both identity/provenance and authority evidence.

### Proposition 9.3 — Hash identity is conditional on canonicalized bytes and named algorithm

A digest claim is meaningless without specifying the exact byte representation and digest algorithm. Semantically equivalent RDF serializations need not have identical bytes.

**Status:** DERIVED.

Future receipt work that hashes semantic graphs must choose either canonical RDF normalization or explicitly hash a particular admitted serialization.

## 10. Proof-obligation matrix

| ID | Property | Current evidence class | Stronger target |
|---|---|---|---|
| PO-01 | exact subject executed | workflow assertion | signed receipt bound to commit/tree |
| PO-02 | pack source non-mutation | qualification filesystem comparison | independent verifier + receipt digest |
| PO-03 | replay convergence | repeated ggen manufacture | cross-runner reproducibility classes |
| PO-04 | navigation position uniqueness | currently model convention | SHACL shape + negative control |
| PO-05 | chapter path confinement | target compiler/filesystem behavior | explicit path gate + SHACL/SPARQL constraint |
| PO-06 | authority separation | workflow permission structure | capability graph + policy verifier |
| PO-07 | evidence closure for standing | procedural interpretation | executable standing derivation over receipt DAG |
| PO-08 | pack composition associativity | conditional model | mechanized algebra for admitted subset |
| PO-09 | receipt integrity | CI logs/metadata | signed or transparency-bound receipt capsule |
| PO-10 | independent reproducibility | same-platform replay | independently reconstructed release capsule |

## 11. Countermodel discipline

For each theorem-shaped statement, the research program should maintain a countermodel or a failing fixture whenever feasible.

Examples:

- omit `ORDER BY` to challenge ordered determinism;
- change the checked-out SHA to challenge exact-head law;
- introduce duplicate navigation positions to challenge totality;
- add a timestamp to a template to challenge replay convergence;
- grant qualification a deployment token to challenge authority separation;
- hand-edit a generated consequence to challenge source singularity;
- mutate pack source during qualification to challenge non-mutation;
- alter the toolchain while reusing an old receipt to challenge evidence equivalence.

A countermodel suite is stronger than a list of principles because it continuously demonstrates that the validators are capable of observing violations.

## 12. Mechanization roadmap

The catalogue suggests three mechanization layers.

### Layer M1 — Graph constraints

Use SHACL or equivalent declarative constraints for local graph properties:

- cardinality;
- allowed kinds;
- path presence;
- position uniqueness;
- namespace and identity constraints.

### Layer M2 — Executable transition contracts

Use repository/runtime checks for properties involving filesystems, toolchains, process isolation, replay, and target compilers.

### Layer M3 — Algebraic and temporal proofs

Use a theorem prover for claims involving:

- evidence closure;
- partial-order standing;
- pack-composition laws;
- authority non-escalation;
- receipt-DAG consistency;
- incremental proof reuse.

The proof assistant should consume identities or generated proof obligations derived from the same admitted source used by runtime qualification. A disconnected formal model would create a second authority rather than strengthen the first.

## 13. Research standard

The book adopts the following rule:

> **Every universal claim must resolve to a definition plus proof obligation; every implementation claim must resolve to executable evidence; every empirical claim must resolve to a protocol and dataset; and every crown must name the exact subject and boundary it crowns.**

This is the point at which the monograph becomes more than architecture documentation. It becomes a program of statements that can be proved, executed, falsified, or retired.
