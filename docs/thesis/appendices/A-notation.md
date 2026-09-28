# Notation, glossary, and symbol table

## 1. Purpose

The monograph uses the same ideas across compiler theory, provenance, process intelligence, security, queueing, marketplace operations, Level-5 maturity, and class closure. This appendix fixes notation so symbols do not drift between chapters.

When implementation names and mathematical names differ, this appendix records the intended correspondence. Mathematics is explanatory unless a repository validator, generated court, or theorem artifact explicitly implements it.

## 2. Core manufacturing symbols

| Symbol | Name | Meaning |
|---|---|---|
| `O` | raw observation | information visible before admission |
| `α` | admission function | partial transition from raw observation to admitted observation |
| `O*` | admitted observation | observation permitted to influence the next lawful transition |
| `μ` | manufacturing function | bounded transformation from admitted subject to artifact consequence |
| `A` | artifact set | materialized consequence of manufacture |
| `S` | exact subject | identity-complete input to a claimed execution |
| `I` | identity/provenance tuple | immutable identities relevant to a claim |
| `G` | semantic graph | admitted RDF graph or graph-equivalent semantic source |
| `Q` | selection program | query/selection logic, commonly SPARQL |
| `T` | template/projection set | bounded artifact-rendering programs |
| `V` | toolchain identity | compiler/generator/validator version or immutable identity |
| `E` | relevant environment | environment attributes that may affect the specified consequence |
| `K` | gate set | admission/refusal predicates |
| `F` | fixture set | qualification consumer/witness inputs |
| `D` | dependency relation | typed dependencies between subjects/packs/receipts |
| `Ω` | authority contract | required/prohibited capabilities for a transition |

Canonical compact equation:

`A = μ(O*)`.

Expanded subject form:

`A = μ(S)` where `S = (I, G, Q, T, V, E)`.

## 3. Transition symbols

The constitutional phase ordering is:

`SELECT → CONSTRUCT → DO`.

A more complete evidence pipeline is:

`OBSERVE → ADMIT → SELECT → CONSTRUCT → VERIFY → DO → RECEIPT → REPLAY → STANDING`.

These arrows do not imply every workflow must be physically serialized. Independent transitions may execute concurrently when dependencies and authority permit.

### `SELECT`

Identifies candidate facts, bindings, plans, or targets. Selection is reversible and does not imply permission to materialize or actuate.

### `CONSTRUCT`

Materializes bounded reversible consequences in the admitted construction domain.

### `VERIFY`

Executes a predicate over the subject or consequence: parser, validator, replay comparator, target compiler, integration test, formal checker, or another bounded court.

### `DO`

Crosses a consequential boundary such as publish, merge, send, deploy, remote mutation, permission change, or production actuation.

## 4. Receipt and standing symbols

| Symbol | Meaning |
|---|---|
| `R` | a receipt/evidence object |
| `R*` | an admissible receipt set for a claim |
| `C` | claim whose standing is being evaluated |
| `σ(C,R*,t)` | standing function at evidence epoch `t` |
| `≡_C` | claim-relative evidence equivalence |
| `≈` | artifact equivalence relation for replay |
| `r1 → r2` | receipt dependency/derivation edge |

Standing vocabulary:

- `UNKNOWN` — evidence does not establish execution or a more precise non-execution state;
- `PARTIAL_ALIVE` — prerequisite/lower boundaries succeeded but the full claim is incomplete or requalifying;
- `ALIVE` — exact admitted subject executed successfully across the full claimed boundary;
- `BLOCKED:<reason>` — a prerequisite/external/authority condition prevented execution;
- `BUILD_BROKEN` — execution reached the relevant build/manufacture boundary and failed;
- `UNSUPPORTED` — requested capability lies outside the supported contract;
- `REFUSED:<code>` — a named admission/policy predicate rejected the transition.

Standing is not a confidence score. It is an evidence-derived classification.

## 5. Pack algebra symbols

A pack is:

`P = (ι, G, Q, T, K, F, D, Ω)`.

| Symbol | Meaning |
|---|---|
| `P,Q,R` | packs |
| `ι` | pack identity tuple |
| `ε` | empty/identity pack in the formal algebra |
| `⊗` | partial pack composition operator |
| `⊔` | semantic graph union when context is clear |
| `⊔_π` | policy-governed partial authority join |
| `τ_P` | target/output ownership relation for pack P |
| `P' ⪯ P` | P' refines/substitutes for P under a declared contract |
| `P' ▷ P` | P' supersedes P with migration obligation |
| `Compat(P,Q)` | conjunction of predicates required before composition is defined |
| `Independent(P,Q)` | packs proven independent for a named operation/claim |
| `Class(P)` | semantic responsibility class of P |
| `P(θ)` | parameterized pack family/profile |

Conditional associativity:

`(P ⊗ Q) ⊗ R ≡ P ⊗ (Q ⊗ R)`

only under the compatibility conditions defined in the pack-algebra chapter.

### Semantic pack classes

- `KernelPack` — canonical reusable calculus/semantic foundation;
- `CapabilityPack` — orthogonal reusable capability;
- `ProfilePack` — product/platform/organization/deployment binding;
- `WorldPack` — executable/simulatable environment and falsifier space;
- `CompatibilityPack` — historical seam retained for consumers;
- `EvidencePack` — receipt/provenance/audit/standing semantics;
- `ReleaseControlPack` — release/publish transition semantics;
- `UmbrellaPack` — stable consumer composition/default entry point.

These are semantic responsibility classes. They are independent of marketplace packaging profiles `projection`, `semantic`, and `project`.

## 6. Level-5 maturity symbols

For pack `P` and exact subject `S`:

`M(P,S) = (m_s, m_a, m_m, m_e, m_r, m_ω, m_c)`

where:

| Coordinate | Meaning |
|---|---|
| `m_s` | semantic-source maturity |
| `m_a` | admission/refusal maturity |
| `m_m` | manufacture maturity |
| `m_e` | real execution-boundary maturity |
| `m_r` | receipt/replay maturity |
| `m_ω` | authority-fence maturity |
| `m_c` | composition/class-closure maturity |

Each coordinate ranges over `L1 < L2 < L3 < L4 < L5`.

The vector is non-compensatory: a high coordinate does not erase a missing required coordinate for a claim.

Documentation object:

`D(P,S) = (T_u, H, R_f, E_x)`

where `T_u` = Tutorial, `H` = How-to, `R_f` = Reference, and `E_x` = Explanation.

Structural Diátaxis closure:

`D_4(P,S) = T_u ∧ H ∧ R_f ∧ E_x`.

Documentation correspondence:

`Corr_D(P,S) = Corr_source ∧ Corr_commands ∧ Corr_generated ∧ Corr_refusals ∧ Corr_authority ∧ Corr_replay`.

Strong Level-5 documentation standing:

`L5Doc(P,S) = D_4(P,S) ∧ Corr_D(P,S) ∧ Exec_D(P,S)`.

These symbols are defined formally in `12-level5-maturity-and-class-closure.md` and operationally in `docs/reference/level5-maturity-contract.md`.

## 7. Graph and ontology terms

### RDF graph

A set of subject-predicate-object triples under RDF semantics. Graph serialization bytes are not identical to graph semantics; multiple serializations can denote the same graph.

### Vocabulary

A collection of IRIs used to name classes, properties, concepts, or other semantic terms.

### Ontology

A formal semantic model describing domain terms and relationships. In this project the word is sometimes used broadly for Turtle semantic source; not every file necessarily uses the full expressive power of OWL.

### Shape

A constraint description, particularly in SHACL, used to validate graph structure/content under declared shape semantics.

### Closed-world manufacturing constraint

A constraint required for manufacture even though absence of a statement in base RDF open-world semantics is not itself falsity.

### Semantic source singularity

Property that a fact intended to govern multiple consequences has one canonical authority and deterministic projections rather than multiple independently editable authorities.

### Class closure

Portfolio property in which repeated semantic/protocol/lifecycle/projection law is canonicalized into stable classes/kernels while non-equivalent domain/world/runtime facts remain explicit profiles or independent classes.

## 8. Compiler terms

### Intermediate representation (IR)

Representation consumed and transformed by a compiler stage. The monograph treats admitted RDF/semantic graph as a high-level IR for target artifact manufacture.

### Projection

A deterministic or equivalence-bounded transformation from selected semantic bindings to a target artifact.

### Target compiler

An independent compiler/interpreter validating generated consequences, e.g. mdBook for generated book control surfaces or Rust tooling for generated Rust source.

### Compiler court

An executable validation boundary whose result is admissible evidence for a specific compilation/manufacture claim.

### Replay convergence

Property that repeated manufacture of an exact subject produces equivalent specified artifacts under the declared equivalence relation.

### Reproducibility

Stronger notion in which another execution environment/party can recreate specified equivalent artifacts from declared source, instructions, and relevant environment. The experimental chapter reports R0–R5 classes rather than using the word without qualification.

## 9. Provenance and security terms

### Subject identity

Immutable identifier(s) for what was executed: commit, tree, pack digest, artifact digest, policy version, or a claim-specific tuple.

### Provenance

Information describing where an entity came from and which activities/agents/inputs contributed to it.

### Authority

Capability and policy context permitting a transition to cause effects. Authority is not identical to provenance.

### Capability

A concrete means by which a principal/process can perform an operation, such as repository write, Pages deploy, secret read, or remote API mutation.

### Ambient authority

Capabilities available implicitly to code rather than passed/admitted for a specific bounded purpose.

### Confused deputy

A condition in which a more privileged component is induced to exercise its authority on behalf of a less privileged or unauthorized subject.

### Receipt

Structured evidence binding subject, boundary, executor, authority, result, consequence, and predecessors.

### Evidence closure

The complete set of admissible receipts required to establish a claim.

### Receipt DAG

Directed evidence graph in which receipts refer to required predecessor evidence or derivation lineage.

## 10. Process-intelligence terms

### Event

Observed occurrence of an activity at a point/interval in time.

### Object

Persistent identifiable entity involved in events, e.g. pack, commit, workflow run, artifact, release.

### OCEL

Object-Centric Event Log: a format/model in which one event can relate to multiple objects, avoiding forced assignment to one case identifier.

### Process state as event closure

Research hypothesis that enough current operational state can be reconstructed from event/object history and semantic relations without a separate independently authoritative workflow-state store.

## 11. Queueing symbols

| Symbol | Meaning |
|---|---|
| `λ` | throughput/arrival rate |
| `L` | average work in process |
| `W` | average lead/cycle time |
| `λ_O` | observation throughput |
| `λ_M` | manufacturing throughput |
| `λ_E` | evidence throughput |
| `λ_D` | consequential actuation throughput |
| `L_M` | construction WIP |
| `L_E` | evidence WIP |
| `L_D` | actuation WIP |
| `WIP_P` | count of open required proof obligations |

Little's Law:

`L = λW`.

The law applies under its steady-state assumptions; it is not a universal instantaneous identity for arbitrary transient repositories.

## 12. Economic metrics

| Symbol | Meaning |
|---|---|
| `Y` | evidence yield: standing consequences / manufactured consequences |
| `L_s` | semantic leverage |
| `L_r` | receipt/evidence reuse leverage |
| `C(Δ)` | total cost of semantic change Δ |
| `C_E` | evidence transaction cost |
| `TTI` | time to validated information about consequence |
| `TTC` | time to authorized external change |

These metrics are research instruments, not yet normative marketplace release metrics.

## 13. Experimental metrics

| Abbreviation | Meaning |
|---|---|
| `MSR` | manufacturing success rate over admitted attempts |
| `RCR` | replay convergence rate |
| `DI` | drift incidence |
| `SL` | semantic leverage |
| `ELT` | evidence lead time |
| `RRR` | receipt reuse rate |
| `BER` | observed boundary escape rate |
| `MTTR` | mean/median time to repair depending report definition |

Every benchmark MUST define denominators and exclusions before interpreting these metrics.

## 14. Reproducibility classes

- `R0` — in-process repeat;
- `R1` — fresh process, same workspace/machine;
- `R2` — fresh workspace, same machine class;
- `R3` — fresh ephemeral runner under same declared environment class;
- `R4` — materially independent provider/infrastructure;
- `R5` — third-party reconstruction from published release capsule.

A result at `R2` MUST NOT be described as though it passed `R5`.

## 15. Proof-status vocabulary

- `DERIVED` — follows under stated definitions/assumptions;
- `EXECUTABLE` — implementation has a validator/court capable of observing the property for exercised subjects;
- `EMPIRICAL` — supported by finite observations;
- `MECHANIZATION CANDIDATE` — precise enough for formal encoding but not mechanically proved;
- `OPEN` — research question or unresolved proposition.

The proof status belongs to the claim, not to the prose chapter as a whole.

## 16. Normative requirement identifiers

Constitution identifiers use:

`GGM-<DOMAIN>-NNN`.

Current domains include:

- `SRC` — source authority;
- `PACK` — pack identity;
- `SEM` — semantic source;
- `PROJ` — projection;
- `ADM` — admission/refusal;
- `ID` — subject identity;
- `AUTH` — authority;
- `QUAL` — qualification;
- `DET` — determinism/reproducibility;
- `RCPT` — receipts;
- `STAND` — standing;
- `COMP` — composition;
- `L5` — Level-5 maturity/class closure;
- `DOC` — documentation/publication;
- `CI` — workflow law;
- `REL` — release law.

## 17. Common distinctions

### Source vs consequence

Source authorizes manufacture; consequence is what manufacture produces.

### Artifact vs evidence

An artifact is produced work. Evidence is information that supports a claim about work or a transition.

### Validation vs proof

A validator establishes a property for an exercised subject under its own soundness assumptions. A mathematical proof establishes a proposition in a formal model. Neither automatically substitutes for the other.

### Deterministic vs correct

A system can deterministically generate the same wrong output.

### Reproducible vs replayed

Replay is one execution relationship; reproducibility includes independent reconstruction under a declared source/environment/instruction contract.

### Authorized vs correct

An authorized action may still be wrong; a correct artifact may still be unauthorized to deploy.

### Packaging profile vs semantic class

`projection|semantic|project` describes bundle shape. Kernel/capability/profile/world/compatibility/evidence/release-control/umbrella describes semantic responsibility.

### Structural Diátaxis vs Level-5 documentation standing

Four documents can exist while contradicting canonical source or lacking executable correspondence. Structural closure is necessary but not sufficient.

### Green workflow vs standing

Workflow success is one receipt. Standing depends on the claim's required evidence closure.

### Blocked vs broken

Blocked means the transition could not execute because a prerequisite/capability was unavailable. Broken means execution reached the relevant boundary and failed.

## 18. Canonical one-page model

```text
RAW WORLD
   │
   ▼
Observation O
   │ α  admission / refusal
   ▼
Admitted subject S = (identity, G, Q, T, V, E)
   │
   ├── SELECT  ── enumerate lawful candidates
   │
   ├── CONSTRUCT via μ ──> artifacts A
   │                         │
   │                         ▼
   │                       VERIFY
   │                         │
   │                         ▼
   └──────────────────────> receipts R
                              │
                              ▼
                    evidence closure / σ
                              │
                   ┌──────────┴──────────┐
                   ▼                     ▼
             no DO authority        admitted DO
                   │                     │
                   ▼                     ▼
             reversible state      external consequence
                                         │
                                         ▼
                                       receipt
                                         │
                                         ▼
                                      standing
```

At portfolio scale, add the class-closure projection:

```text
canonical kernels/classes
      + orthogonal capabilities
      + umbrellas/defaults
      + parameterized profiles/worlds
      → many pack instances with fewer independent semantic authorities
```

This is the semantic center of the book. Every specialized chapter elaborates one portion without changing the fundamental distinction between **what is known, what may be constructed, what may be done, what class owns the truth, and what has actually been proved by observed execution**.
