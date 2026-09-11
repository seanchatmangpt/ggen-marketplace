# Level-5 maturity, Diátaxis correspondence, and class closure

## 1. Research problem

A software marketplace can grow in two very different ways.

In the first, every new capability arrives as another independent bundle containing its own vocabulary, templates, tests, documentation, release rules, and operational assumptions. Directory count increases, but so does semantic duplication. The marketplace becomes a pile of generators whose apparent reuse hides a growing number of competing authorities.

In the second, repeated law is factored into canonical semantic classes and orthogonal capabilities. Product, environment, and world-specific facts remain parameterized profiles over that shared law. Documentation, qualification, receipts, and standing remain attached to the exact subject that actually executed.

This chapter calls the second condition **class closure** and treats it as the composition dimension of Level 5.

The central research claim is narrower than “Level 5 means mature.” It is:

> A reusable pack family reaches its strongest maturity only when semantic authority, admission, deterministic manufacture, real execution evidence, receipt/replay, authority containment, composition, and documentation correspondence close over the same exact subject.

No single green check can establish that closure.

## 2. Maturity as a vector, not a scalar

Let a pack subject be `P@S`, where `S` binds exact source, dependencies, toolchain, configuration, and relevant environment.

Define seven maturity dimensions:

`M(P,S) = (m_s, m_a, m_m, m_e, m_r, m_ω, m_c)`

where:

- `m_s` — semantic-source maturity;
- `m_a` — admission/refusal maturity;
- `m_m` — manufacture maturity;
- `m_e` — execution maturity;
- `m_r` — receipt/replay maturity;
- `m_ω` — authority-fence maturity;
- `m_c` — composition/class-closure maturity.

Each coordinate ranges over five ordered levels:

`L1 < L2 < L3 < L4 < L5`.

The coordinates are intentionally not averaged. A pack with six L5 coordinates and one L2 consequential authority coordinate is not “4.6/5 mature.” The missing authority coordinate remains a real missing boundary.

### Proposition 2.1 — non-compensability

Let `Req(C)` be the set of maturity predicates required by claim `C`. If any required predicate is unestablished, stronger evidence on another independent coordinate cannot establish `C`.

Formally, if:

`C ⇒ P_i`

and `P_i` is not established, then for any evidence set establishing `{P_j | j ≠ i}`:

`not_proven(C)`.

This follows from ordinary proof closure: independent premises do not compensate for a missing required premise.

**Engineering consequence:** maturity dashboards should show the vector or lattice position rather than collapsing it into a misleading mean.

## 3. The five levels

The operational reference defines the full 5 × 7 table. This chapter focuses on what changes conceptually at each level.

### L1 — specimen

The capability exists as a useful example or manually understandable artifact. Semantic authority, admission, replay, and composition may be implicit.

L1 is not pejorative. A specimen can be valuable research material. Its limitation is that the consumer must reconstruct much of the contract from context.

### L2 — structured

Identity, schemas, templates, examples, and boundaries become inspectable. The capability is reusable with manual interpretation, but representation drift remains possible.

### L3 — admitted

The semantic subject becomes machine-readable and fail-closed enough for bounded manufacture. RDF/canonical models, deterministic gates, explicit dependencies, and typed refusals begin replacing convention.

### L4 — executable

The claimed behavior is exercised against a real consumer/runtime boundary. Manufacture converges, receipts/replay are verifiable for the claimed scope, and authority phases are explicit.

### L5 — class-closed

The capability is no longer merely a good individual pack. Its reusable semantics are factored into a stable class/kernel, composition conflicts are explicit, product/world variation is parameterized rather than cloned, authority does not widen by union, and evidence/doc correspondence closes over exact subjects.

L5 therefore adds a **portfolio property** to individual-pack quality.

## 4. Documentation as a correspondence system

Define the documentation object:

`D(P,S) = (T_u, H, R_f, E_x)`

where:

- `T_u` — Tutorial;
- `H` — How-to;
- `R_f` — Reference;
- `E_x` — Explanation.

The four elements are not interchangeable because they solve different information problems.

### Tutorial

A tutorial teaches a real path. The strongest tutorial claim is not “the commands are plausible,” but:

`documented_path(P,S) = executed_path(P,S)`

for the bounded subject the tutorial claims.

### How-to

A how-to is a goal-directed transition contract. For consequential tasks it must make the authority ceiling, refusal conditions, receipt, falsifiers, and rollback visible.

### Reference

Reference should be the lowest-entropy prose projection of canonical source. Facts already derivable from RDF, manifests, admitted configuration, schemas, and gates should not be re-authored as a competing registry.

### Explanation

Explanation preserves why the system has its fences. A Level-5 explanation should record the preservation target, Chesterton fence, calculus, exclusions, falsifiers, extension law, and operationalization.

## 5. Diátaxis closure

Define structural Diátaxis closure:

`D_4(P,S) = T_u ∧ H ∧ R_f ∧ E_x`.

This proves only that all four information functions are represented. Strong documentation standing additionally requires correspondence:

`Corr_D(P,S)`.

A useful decomposition is:

`Corr_D = Corr_source ∧ Corr_commands ∧ Corr_generated ∧ Corr_refusals ∧ Corr_authority ∧ Corr_replay`.

Then:

`L5Doc(P,S) = D_4(P,S) ∧ Corr_D(P,S) ∧ Exec_D(P,S)`

where `Exec_D` means the executable paths claimed by documentation have real witnesses at their stated boundary.

### Proposition 5.1 — documentation existence is weaker than documentation correspondence

The existence of four non-empty documents does not imply `Corr_D`.

**Counterexample:** a reference page can state a timeout copied from an obsolete configuration while all four quadrants still exist. Therefore structural completeness is necessary but insufficient.

### Proposition 5.2 — generated reference reduces duplicated-authority state space

If a reference fact is deterministically projected from canonical semantic/configuration source, then independent edit states between source and reference are removed for that fact, subject to correctness of the projection.

This is the documentation analogue of semantic source singularity.

## 6. Generic maturity infrastructure and domain semantics

A reusable maturity pack faces a Rice-like boundary: it can manufacture generic checks over mechanics it can observe, but it cannot decide or invent arbitrary domain correctness from pack existence alone.

`pack-maturity-pack` therefore supplies generic infrastructure for:

- fixed-point regeneration;
- receipt verification;
- Diátaxis structure/correspondence obligations.

It does not infer:

- what the domain invariant should be;
- which mutation is a meaningful negative witness;
- whether a cloud deployment succeeded;
- whether a benchmark claim is fair;
- whether a customer accepted a result;
- who owns consequential DO authority.

This separation is essential. A generic maturity framework that fills missing domain evidence with plausible defaults would increase documentation coverage while decreasing epistemic quality.

## 7. Pack classes

Let `Class(P)` describe the primary semantic responsibility of pack `P`, independently of its packaging profile.

The marketplace distinguishes at least:

- **KernelPack** — canonical reusable calculus/semantic foundation;
- **CapabilityPack** — orthogonal reusable capability over a kernel/public vocabulary;
- **ProfilePack** — product/platform/organization/deployment binding of shared law;
- **WorldPack** — executable/simulatable environment, information partition, action space, falsifiers;
- **CompatibilityPack** — historical seam retained for existing consumers;
- **EvidencePack** — receipt/provenance/audit/standing semantics;
- **ReleaseControlPack** — release/publish state transition semantics;
- **UmbrellaPack** — stable composition/default entry point over modules.

A pack's profile (`projection`, `semantic`, `project`) answers “how is this bundle packaged?” Its class answers “what semantic responsibility does this bundle own?” Conflating the two prevents useful composition analysis.

## 8. Class closure

For a family `F = {P_1, …, P_n}`, define the union of asserted semantic authority:

`S_F = ⋃ S(P_i)`.

Let `dup_F(x)` be the number of independent canonical owners of semantic fact/class/rule `x` within the family.

A class-closure objective minimizes unnecessary duplicate ownership while preserving non-equivalent domain semantics:

`min Σ_x max(0, dup_F(x) - 1)`

subject to:

- consumer compatibility;
- target ownership compatibility;
- admission/refusal preservation;
- toolchain/runtime feasibility;
- authority non-escalation;
- provenance preservation.

This is not “merge everything.” It is a constrained factoring problem.

## 9. Consolidation morphisms

Useful family transformations include:

### 9.1 Canonicalization

Move duplicated vocabulary/protocol truth into one kernel:

`P_i, P_j → K + P_i' + P_j'`

where `P_i'` and `P_j'` retain only their semantic/runtime deltas.

### 9.2 Capability extraction

Factor behavior shared by several siblings into an orthogonal module:

`P_i → K ⊗ C_a ⊗ Profile_i`.

### 9.3 Umbrella formation

Create a stable consumer bundle:

`U = compose(K, C_1, …, C_k, defaults)`.

`U` should own composition/default selection, not duplicate the semantic authority already owned by `K` and `C_i`.

### 9.4 Profile conversion

When variation is data rather than behavior:

`P(θ)`

is preferable to many clones `P_1, P_2, …` whose only difference is an environment/product ABox.

### 9.5 Supersession

For a legacy pack `L` and successor `N`:

`N ▷ L`

requires a consumer migration witness or explicit incompatible consumer classes. Deprecation without successor/migration evidence is not class closure.

## 10. Consolidation equivalence boundary

Two packs with similar names are not necessarily equivalent. Define the comparison tuple:

`E(P,Q) = (S, G, A, X, R, Ω, C)`

where:

- `S` — semantic authority;
- `G` — generated target ownership;
- `A` — admission/refusal behavior;
- `X` — runtime/execution boundary;
- `R` — receipt/replay obligations;
- `Ω` — authority ceiling;
- `C` — consumers/compatibility.

A physical merge is justified only for the subset of this tuple proven compatible for the intended successor contract.

One failed edge does not invalidate the whole family factoring problem. It means the family graph contains a boundary that must remain explicit.

## 11. Authority under class closure

Authority is the easiest property to widen accidentally during consolidation.

Suppose two modules have construction authority sets `Ω_C(P)` and `Ω_C(Q)`. A naive umbrella might expose:

`Ω(P ⊗ Q) = Ω(P) ∪ Ω(Q)`.

That is unsafe because a combination may enable a consequential transition neither module could perform alone.

Instead require a policy-governed partial join:

`Ω(P) ⊔_π Ω(Q) ⇀ Ω(PQ)`.

For a construction-only umbrella:

`Ω(PQ) ⊆ ConstructionCeiling`.

### Proposition 11.1 — class closure must be authority non-expansive unless separately admitted

If a consolidation claims semantic equivalence/preservation and does not introduce a new authority contract, then any new consequential capability in the successor falsifies the preservation claim.

This turns “umbrella accidentally got deploy credentials” into a formal consolidation failure rather than a documentation concern.

## 12. Portfolio-level consolidation opportunities

The marketplace's current pack inventory exhibits recurring structural families. The following are consolidation hypotheses, not deletion orders.

### UI projection family

Many shadcn, React, deck.gl, Remotion, and product-specific UI packs likely share projection grammar while differing mainly in domain state and rendering profiles.

Candidate structure:

```text
ui-projection-kernel
  + render capabilities {shadcn, react, deckgl, remotion, extension}
  + product/domain profiles
```

The DDUI authority law is especially important: presentation must not become a source of domain or DO authority.

### Repository lifecycle family

`as-found`, load-path, intervention, reconciliation, and dogfood lifecycle concepts are naturally states/morphisms of one reconstitution calculus rather than independent semantic authorities.

### Release family

Dry-run publication, release, post-release, cargo CI/CD, GitHub Actions, and ecosystem release gates should share one release-state/authority calculus while retaining platform profiles.

### Enterprise architecture family

TOGAF/enterprise/Fortune-5 architecture concepts should share canonical architecture vocabulary with organization/product/deployment/testing profiles rather than duplicate core architecture facts.

### MCP family

FastMCP, rmcp, gdmcp, mcpp, and bridge packs should share canonical protocol semantics while preserving independent runtime implementations.

### TCPS and wasm4pm families

Both exhibit modular capability sets suitable for explicit umbrellas. The umbrella becomes the normal consumer entry point; capability modules remain individually composable.

### Assurance/reconstitution family

Evidence, certification, SOC2, legacy assurance, and reconstitution packs should share receipt/standing/provenance mathematics without conflating their distinct courts or subjects.

## 13. Consolidation court

A future machine-readable marketplace court should project a graph of classes, target ownership, dependencies, supersession, and consumers and emit typed findings such as:

```text
DUPLICATE_SEMANTIC_AUTHORITY
TARGET_OWNERSHIP_CONFLICT
ORPHAN_PROFILE
UMBRELLA_CYCLE
LEGACY_WITHOUT_SUCCESSOR
SUCCESSOR_WITH_UNMIGRATED_CONSUMER
CLASS_WITHOUT_CANONICAL_KERNEL
AUTHORITY_JOIN_WIDENED
```

The court should **diagnose**, not automatically delete. Deletion remains an irreversible transition gated by migration evidence.

## 14. Level-5 promotion as evidence closure

For claim `C_L5(P,S)`, define required predicates:

`Req_L5 = {Sem, Admit, Manufacture, Execute, Receipt, Authority, Compose, Docs}`.

Then:

`ALIVE(C_L5(P,S))`

requires admissible receipts for every required predicate over equivalent exact subjects and compatible evidence epochs.

A generated Diátaxis tree may establish `Docs_structural`; a successful all-pack qualification may establish `Manufacture` and bounded replay; a native consumer test may establish one `Execute` predicate. None individually implies the full closure.

This makes Level 5 a proof DAG rather than a label.

## 15. Relationship to DfCM

Class closure is a direct application of combinatorial maximalism.

The objective is not premature global simplification. It is to preserve the maximum set of reversible lawful combinations while removing duplicate authority that creates artificial state space.

A good factoring therefore maximizes:

- reusable canonical semantics;
- orthogonal capability composition;
- parameterized profiles;
- explicit conflict/refusal edges;
- reversible construction before irreversible deletion/supersession.

It minimizes:

- duplicated semantic authority;
- hidden defaults;
- ambient namespaces;
- authority union;
- hand-maintained parallel docs/catalogs;
- irreversible migrations before consumer equivalence is proved.

## 16. Falsification program

The Level-5/class-closure model should be rejected or narrowed if experiments show that:

1. class factoring increases semantic coordination cost more than it reduces duplicate drift;
2. shared kernels become universal bottlenecks or unstable mega-ontologies;
3. family profiles cannot express important runtime differences without hidden escape hatches;
4. umbrella composition repeatedly widens authority;
5. generated Diátaxis produces structurally complete but misleading documentation;
6. domain teams routinely need to fork canonical classes because the shared semantics are wrong;
7. exact-subject evidence closure costs more than the defects it prevents for the target class of systems;
8. migration/compatibility burdens make consolidation net-negative.

A Level-5 program is scientific only if these outcomes remain admissible.

## 17. Operational consequence

The marketplace should evolve from:

```text
many directories ≈ many authorities
```

toward:

```text
few canonical classes/kernels
+ many orthogonal capabilities
+ explicit umbrellas
+ many parameterized profiles/worlds
+ exact evidence per boundary
```

The number of pack instances may continue increasing dramatically. The maturity improvement is that the **semantic coordination graph grows sublinearly relative to the instance graph** because repeated truth is represented once and projected/composed lawfully.

## 18. Research status

The 5 × 7 maturity contract and Level-5 Diátaxis infrastructure are executable engineering specifications in the marketplace. The class taxonomy and consolidation calculus are currently a formalized design and operational procedure; portfolio-wide machine-readable class assertions, consumer graph extraction, and automated consolidation courts remain implementation work.

Accordingly:

- **Level-5 documentation structure:** executable/mechanized in `pack-maturity-pack` for its claimed structural boundary;
- **5 × 7 scoring model:** operational specification, with individual scores requiring evidence;
- **class taxonomy:** operational reference, machine-readable portfolio annotations incomplete;
- **class-closure optimizer/court:** OPEN implementation;
- **portfolio consolidation benefits:** plausible and testable, not yet established as a universal empirical result.

This status is intentional. The purpose of Level 5 is not to make the marketplace sound finished. It is to make the remaining incompleteness computable.
