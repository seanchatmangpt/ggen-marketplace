# Normative constitution

## 1. Status of this chapter

This chapter extracts the repository's architectural doctrine into a compact normative specification. It is intended to become progressively executable: each requirement should either map to an existing validator/court, map to a planned validator with a named gap, or be removed if it cannot be operationalized.

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **NOT RECOMMENDED**, **MAY**, and **OPTIONAL** are to be interpreted as described by BCP 14 (RFC 2119 and RFC 8174) when, and only when, they appear in all capitals.

This constitution does not supersede executable repository policy. Where prose and admitted executable law disagree, the discrepancy is a defect to resolve; prose is not authority merely because it is called normative.

## 2. Constitutional objects

The marketplace governs these objects:

- **marketplace** — the admitted registry source and policy;
- **pack** — a reusable semantic manufacturing contract;
- **pack profile** — packaging shape (`projection`, `semantic`, or `project`);
- **pack class** — semantic responsibility such as kernel, capability, profile/world, compatibility, evidence, release-control, or umbrella;
- **consumer** — an admitted subject that invokes one or more packs;
- **artifact** — a manufactured consequence;
- **gate** — a predicate that can admit or refuse a subject;
- **receipt** — evidence about an observed transition;
- **standing** — evidence-derived status of a claim;
- **actuation** — a consequential external transition;
- **Diátaxis surface** — Tutorial, How-to, Reference, or Explanation projection bound to the same contract;
- **release capsule** — a bounded collection of source identity, toolchain identity, artifacts, and receipts sufficient for independent verification under a declared reproducibility class.

## 3. Source authority

### GGM-SRC-001 — Single semantic authority

A fact that is projected into generated consequences **SHOULD** have one canonical authoritative representation unless independent authority is an explicit requirement.

### GGM-SRC-002 — Generated consequences

Generated files **MUST NOT** silently become a second source of truth merely because they are committed for reviewability.

### GGM-SRC-003 — Source hierarchy

The repository **MUST** define where marketplace policy, pack identity, ontology, templates, gates, fixtures, documentation control source, and generated consequences belong.

### GGM-SRC-004 — No hidden generated metadata namespace

Repository conventions that prohibit a generated metadata namespace **MUST** be enforced by validation rather than documentation alone.

### GGM-SRC-005 — No pack symlinks

Pack source **MUST NOT** use symlink indirection where repository policy forbids it. A pack archive/fingerprint **MUST** describe the files actually admitted.

### GGM-SRC-006 — Volatile operational facts

Runtime release identities, asset digests, worker counts, timeout bounds, and other executable marketplace configuration **MUST NOT** be independently copied into scripts or normative documentation when `marketplace.toml` is the admitted source of truth.

## 4. Pack identity

### GGM-PACK-001 — Directory identity

A pack directory name **MUST** equal the pack's declared canonical name.

### GGM-PACK-002 — Version identity

A pack **MUST** declare a version conforming to repository version policy.

### GGM-PACK-003 — Exact source identity

Qualification evidence **MUST** bind to the exact admitted pack source or a cryptographic fingerprint produced by the repository's canonical procedure.

### GGM-PACK-004 — Description is metadata, not proof

Catalog metadata **MUST NOT** be interpreted as evidence that a pack manufactures successfully.

### GGM-PACK-005 — Profile/class separation

A packaging profile **MUST NOT** be treated as a semantic responsibility class, maturity level, or standing state.

## 5. Semantic source

### GGM-SEM-001 — Explicit graph source

A semantic projection pack **SHOULD** make its canonical semantic source explicit and inspectable.

### GGM-SEM-002 — Public vocabulary reuse

Existing public vocabularies **SHOULD** be reused when their semantics fit. Local vocabulary **SHOULD** be limited to irreducible marketplace/domain concepts.

### GGM-SEM-003 — Constraint separation

Knowledge representation and manufacturing constraints **MUST NOT** be conflated. Closed-world manufacturing invariants **MUST** be expressed by gates, shapes, or equivalent validation when base RDF semantics do not provide them.

### GGM-SEM-004 — Ordered semantics

When result order affects artifact meaning, the selection/projection contract **MUST** define a deterministic order.

## 6. Projection

### GGM-PROJ-001 — Declared targets

Each generated artifact **MUST** have a declared target path or target rule.

### GGM-PROJ-002 — Bounded writes

Manufacture **MUST NOT** write outside its admitted consumer/output boundary.

### GGM-PROJ-003 — Source non-mutation

Qualification **MUST** reject a pack whose manufacture mutates the admitted pack source, unless mutation is explicitly part of a different contract and isolated from qualification.

### GGM-PROJ-004 — No implicit multi-writer

Two packs **MUST NOT** own the same output path unless a deterministic merge operator and conflict policy are admitted.

### GGM-PROJ-005 — Replay

A consequential pack qualification **MUST** include replay appropriate to the claimed determinism class.

## 7. Admission and refusal

### GGM-ADM-001 — Observation is not admission

Raw observation **MUST NOT** influence manufacture as though it were admitted merely because it is available to the process.

### GGM-ADM-002 — Fail closed

When the system cannot determine which configuration schema, authority rule, or manufacturing contract applies, it **MUST** refuse rather than guess.

### GGM-ADM-003 — Typed refusal

Where practicable, refusal **SHOULD** use a stable machine-readable code that identifies the failed predicate family.

### GGM-ADM-004 — Unsupported is distinct

A request outside the available capability contract **MUST NOT** be represented as a build failure if no execution was possible.

## 8. Exact-subject evidence

### GGM-ID-001 — Exact commit/tree

CI evidence used for a pull request or release **MUST** bind to the immutable subject actually executed.

### GGM-ID-002 — Branch names are insufficient

A mutable branch name **MUST NOT** be the only source identity in a durable receipt.

### GGM-ID-003 — Exact-head assertion

Where concurrent branch motion could cause ambiguity, the workflow **MUST** assert that checked-out source identity equals the claimed subject identity before crown-bearing execution.

### GGM-ID-004 — Evidence transfer

Evidence from subject `S1` **MUST NOT** crown subject `S2` without an explicit equivalence proof covering every claim-relevant difference.

## 9. Authority

### GGM-AUTH-001 — SELECT/CONSTRUCT/DO separation

Selection, reversible construction, and consequential actuation **MUST** be distinguishable operations in any workflow that can mutate external state.

### GGM-AUTH-002 — Zero unreceipted actuation

Consequential `DO` **MUST** produce or be bound to a receipt sufficient to identify subject, authority, boundary, and result.

### GGM-AUTH-003 — Least construction authority

Construction **SHOULD NOT** possess deployment, merge, secret-bearing, or remote-write capabilities unless required by its explicit bounded contract.

### GGM-AUTH-004 — No authority by composition

Composing packs or workflows **MUST NOT** automatically union authority sets. Capability joins **MUST** be governed by explicit policy.

### GGM-AUTH-005 — Qualification is not deployment

A qualification court **MUST NOT** imply publication/deployment authority merely because the generated artifact passed validation.

## 10. Qualification

### GGM-QUAL-001 — Real runtime

Consequential pack behavior **SHOULD** be qualified with the admitted real ggen runtime rather than only mocked or structurally inspected.

### GGM-QUAL-002 — Isolated consumer

Qualification **SHOULD** exercise a bounded consumer environment so source mutation, target generation, and replay can be observed without relying on repository incidental state.

### GGM-QUAL-003 — Fixture independence

A synthetic fixture **MUST NOT** be treated as proof of real-consumer integration. Self-hosting or external-consumer evidence **SHOULD** supplement generic qualification for critical packs.

### GGM-QUAL-004 — Negative controls

Crown-bearing validators **SHOULD** have negative controls demonstrating that representative violations are actually detected.

### GGM-QUAL-005 — No vacuous green

A validation court **MUST NOT** claim success if the relevant subject set was empty, skipped, or silently not exercised when the claim requires execution.

## 11. Determinism and reproducibility

### GGM-DET-001 — Equivalence relation

Every replay/reproducibility claim **MUST** identify the artifact equivalence relation.

### GGM-DET-002 — Relevant environment

Any environmental factor that changes the specified artifact **MUST** be treated as part of the relevant subject/environment, removed as nondeterminism, or explicitly excluded from the claim.

### GGM-DET-003 — Stronger terms require stronger evidence

A same-runner replay **MUST NOT** be labeled independent reproducibility. Reports **SHOULD** use the R0–R5 classes defined by the experimental-method chapter.

### GGM-DET-004 — Deterministic archive/catalog

Marketplace catalog and archive projections that claim determinism **MUST** be reconstructed and compared under the repository's admitted procedure.

## 12. Receipts

### GGM-RCPT-001 — Subject binding

A receipt **MUST** identify the exact subject or an unambiguous digest/identity tuple.

### GGM-RCPT-002 — Boundary binding

A receipt **MUST** identify which transition or validation boundary executed.

### GGM-RCPT-003 — Toolchain binding

A receipt **SHOULD** identify the executor/toolchain versions relevant to the claim.

### GGM-RCPT-004 — Consequence binding

A receipt for materialized artifacts **SHOULD** include digests or equivalent immutable artifact identifiers.

### GGM-RCPT-005 — Predecessor closure

A crown whose proof depends on predecessor receipts **MUST NOT** be assigned if the required evidence closure is incomplete.

### GGM-RCPT-006 — Algorithm naming

Every cryptographic digest **MUST** name its algorithm and byte/canonicalization domain.

## 13. Standing

### GGM-STAND-001 — Claim scope

Standing **MUST** be attached to a specific claim and boundary, not to a repository as an unqualified scalar property.

### GGM-STAND-002 — `ALIVE`

`ALIVE` **MUST** require observed successful execution of the exact admitted subject across the full boundary of the claim.

### GGM-STAND-003 — `PARTIAL_ALIVE`

`PARTIAL_ALIVE` **SHOULD** be used when prerequisite or lower-level boundaries succeeded but at least one required higher boundary remains unexecuted or unresolved.

### GGM-STAND-004 — `BUILD_BROKEN`

`BUILD_BROKEN` **MUST** mean execution reached the claimed build/manufacture boundary and failed there; it **MUST NOT** be used for a missing tool or unavailable permission that prevented execution.

### GGM-STAND-005 — `BLOCKED`

`BLOCKED` **SHOULD** identify a prerequisite or external condition that prevented the requested transition.

### GGM-STAND-006 — Historical versus current standing

Historical execution receipts **MAY** remain valid observations while current standing changes because subject, dependency, policy, environment, or validity epoch changed.

## 14. Composition

### GGM-COMP-001 — Partial composition

Pack composition **MUST** be treated as potentially undefined. An incompatible pair **MUST** refuse rather than rely on accidental file order or overwrite behavior.

### GGM-COMP-002 — Cross-pack qualification

Independent qualification receipts **MUST NOT** crown a composed subject when the packs can interact through graph, targets, dependencies, or authority.

### GGM-COMP-003 — Dependency typing

The architecture **SHOULD** distinguish semantic reference, construction dependency, qualification dependency, and actuation dependency.

### GGM-COMP-004 — Incremental reuse

Receipt reuse **MAY** reduce validation work only when unchanged proof dependencies and equivalence conditions are established.

### GGM-COMP-005 — Class closure before duplication

When multiple packs independently own semantically equivalent protocol, lifecycle, maturity, authority, or projection law, contributors **SHOULD** factor the shared authority into a canonical kernel/capability rather than create another independent copy.

### GGM-COMP-006 — Preserve non-equivalence

Class closure **MUST NOT** erase domain/world/runtime/compatibility differences unless equivalence or supersession has been established for the affected consumer contract.

## 15. Level-5 maturity and class closure

### GGM-L5-001 — Vector, not average

Level-5 maturity **MUST** be evaluated as claim-relevant closure across semantic source, admission, manufacture, execution, receipt/replay, authority fencing, and composition. A stronger result on one dimension **MUST NOT** compensate for a missing required dimension.

### GGM-L5-002 — Exact-subject crown

A Level-5 standing claim **MUST** bind the exact subject and the exact boundaries executed. Pack name, version label, directory existence, generated documentation, or historical CI success are insufficient.

### GGM-L5-003 — Diátaxis closure

A Level-5 capability **MUST** expose Tutorial, How-to, Reference, and Explanation surfaces whose claims correspond to the same admitted semantic/manufacturing contract.

### GGM-L5-004 — Structural docs are not execution

A generated four-quadrant Diátaxis tree **MUST NOT** be interpreted as proof of domain behavior, external-system effect, or consequential authority without the corresponding execution evidence.

### GGM-L5-005 — Generic maturity infrastructure cannot invent domain facts

A generic maturity/qualification pack **MUST NOT** manufacture missing domain invariants, negative witnesses, benchmark outcomes, customer acceptance, cloud observations, or DO authority from the absence of domain evidence.

### GGM-L5-006 — Pack class is explicit

A Level-5 family **SHOULD** identify canonical semantic responsibility using pack classes and explicit composition/supersession relations rather than relying on names or directory shape.

### GGM-L5-007 — Consolidation requires equivalence or migration evidence

Physical merge, deletion, or supersession of overlapping packs **MUST NOT** occur solely from naming/structural similarity. The transition **MUST** preserve or explicitly migrate semantic authority, target ownership, admission/refusal behavior, runtime/toolchain requirements, receipt obligations, authority ceilings, provenance, and affected consumers.

### GGM-L5-008 — Authority non-escalation under consolidation

A class-closure/umbrella transition **MUST NOT** widen consequential authority unless a distinct authority contract is admitted and receipted.

### GGM-L5-009 — Typed consolidation findings

Where mechanized, consolidation analysis **SHOULD** emit typed findings for duplicate semantic authority, target conflicts, orphan profiles, umbrella cycles, missing successors, unmigrated consumers, missing kernels, and authority widening rather than mutating the corpus automatically.

### GGM-L5-010 — Requalification after semantic/documentation drift

A change to claim-relevant semantic source, admission, manufacturer/toolchain, runtime, authority, composition, or Level-5 documentation correspondence **MUST** invalidate/requalify the affected standing closure.

## 16. Documentation and publication

### GGM-DOC-001 — Diátaxis preservation

Tutorial, How-to, Reference, and Explanation documents **MUST** remain distinct in purpose for Level-5 surfaces. Research synthesis **MAY** cross-reference them but **SHOULD NOT** erase their operational roles.

### GGM-DOC-002 — Generated navigation

When book navigation is modeled semantically, `SUMMARY.md` **MUST** remain a generated consequence rather than an independently edited authority.

### GGM-DOC-003 — Target compiler

The generated documentation control surface **MUST** be accepted by the actual pinned target compiler before the book-build boundary can receive `ALIVE` standing.

### GGM-DOC-004 — Publication is distinct

A successful static book build **MUST NOT** be reported as successful public deployment until the publication actuator executes and returns evidence.

### GGM-DOC-005 — Reference anti-duplication

Exact reference facts that have an admitted executable source **SHOULD** be projected or linked to that source rather than copied as independently maintained volatile prose.

### GGM-DOC-006 — Documentation authority ceiling

Documentation generation, rendering, and publication **MUST NOT** grant semantic or consequential authority beyond the source/actuation contracts that produced them.

## 17. CI and workflow law

### GGM-CI-001 — Workflow definition is not execution

The existence or syntax validity of a workflow file **MUST NOT** be treated as evidence that the workflow succeeded.

### GGM-CI-002 — Pinned consequential actions

Consequential third-party workflow actions **SHOULD** be pinned to immutable identities according to repository supply-chain policy.

### GGM-CI-003 — Time bounds

Automated courts **SHOULD** declare finite timeout bounds so a hung validator becomes an observable failure rather than unbounded WIP.

### GGM-CI-004 — No CI self-correction

Validation CI **MUST NOT** silently rewrite and push corrections to pack source unless such mutation is a distinct explicitly authorized workflow.

## 18. Release law

### GGM-REL-001 — Release subject

Every release **MUST** identify the source snapshot it represents.

### GGM-REL-002 — Release capsule

A research-grade release **SHOULD** publish enough source/toolchain/evidence metadata for an independent verifier to reconstruct at least the claimed reproducibility class.

### GGM-REL-003 — Missing evidence is explicit

Release notes **MUST NOT** imply execution of boundaries that were skipped. Missing higher-tier evidence **SHOULD** remain visible as `UNKNOWN`, `BLOCKED`, or another accurate standing.

## 19. Requirement-to-enforcement matrix

The constitution should progressively become a machine-readable matrix with one row per requirement:

| Requirement | Current enforcement | Negative control | Receipt field | Standing dependency |
|---|---|---|---|---|
| GGM-PACK-001 | marketplace validator | mismatched directory/name | `subject.pack` | admission |
| GGM-PROJ-003 | qualification court | pack source mutation | source/consequence digests | qualification |
| GGM-ID-003 | exact-head workflow assertion | deliberate SHA mismatch | `subject.commit/tree` | all CI crowns |
| GGM-AUTH-005 | workflow permissions/jobs | deploy from PR qualification | authority witness | deployment |
| GGM-DOC-003 | `mdbook build` | malformed generated summary | target-compiler result | book build |
| GGM-L5-003 | generated `L5-DOC-*` structural court | missing quadrant/required marker | documentation correspondence | Level-5 docs |
| GGM-L5-005 | generic maturity-pack scope + domain courts | absent domain fact/witness | domain evidence refs | Level-5 domain claim |
| GGM-L5-007 | consolidation procedure; machine court OPEN | incompatible consumer/target/authority pair | migration/equivalence receipt | class closure |
| GGM-L5-008 | authority policy + consolidation review | umbrella authority widening | authority before/after | class closure/DO |

Rows without enforcement are explicit research/engineering gaps, not implied guarantees.

## 20. Constitutional amendment rule

A rule SHOULD be changed when one of the following is true:

- executable evidence repeatedly shows the rule is impractical or incorrectly scoped;
- a stronger public standard subsumes the local rule;
- the rule cannot be operationalized and therefore creates false confidence;
- a threat model or incident exposes a missing invariant;
- composition requires a more precise typed distinction.

Amendments SHOULD preserve historical receipts by versioning the policy identity used to derive standing.

## 21. Constitutional principle

The constitution reduces to one governing invariant:

> **No artifact acquires more semantic authority, execution authority, or evidentiary standing than is justified by its admitted source, explicit transition contract, and observed receipts.**

Level 5 adds one portfolio corollary:

> **No pack family acquires class closure merely by accumulation: repeated truth is canonicalized, non-equivalence remains explicit, and every maturity crown stays bounded by exact evidence.**

Everything else in the marketplace is an implementation of those bounds.
