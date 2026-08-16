# Pack algebra and compositional semantics

## 1. Why an algebra is required

A marketplace with a handful of independent templates can rely on convention. A marketplace intended to manufacture large systems cannot. Once packs depend on other packs, share ontology, target the same files, contribute policy, or carry different authority requirements, composition itself becomes a semantic operation.

This chapter defines a **partial algebra of packs**. “Partial” is essential: not every pair of packs should compose. A conflict that cannot be admitted explicitly is not an inconvenience to be hidden by merge order; it is information about the boundary of the current manufacturing system.

The goal is not to force every implementation detail into category theory. The goal is to establish enough mathematics that the marketplace can answer five concrete questions mechanically:

1. Can these packs compose?
2. If they compose, what is the resulting semantic subject?
3. Which outputs may each pack own?
4. Which evidence must be re-established after composition?
5. Can prior receipts be reused without unsoundly widening their claim?

## 2. Pack as a typed manufacturing object

Define a pack:

`P = (ι, G, Q, T, K, F, D, Ω)`

where:

- `ι` — immutable pack identity: name, version, source digest, provenance;
- `G` — semantic graph contributed or required by the pack;
- `Q` — named selection programs over admitted graph state;
- `T` — bounded projections from selected bindings to artifacts;
- `K` — gates and refusal predicates;
- `F` — qualification fixtures or consumer witnesses;
- `D` — declared dependency relation;
- `Ω` — authority requirements and prohibited capabilities.

A marketplace pack directory is a concrete serialization of part of this tuple. Some components may be implicit today; the algebra describes what must eventually become explicit if composition is to be reasoned about rather than guessed.

## 3. Pack identity

Pack identity has at least four levels.

### 3.1 Logical identity

`id_L(P) = (name, version)`

Useful for catalog and dependency resolution, but insufficient for execution evidence because source may differ while logical identity remains unchanged.

### 3.2 Source identity

`id_S(P) = digest(admitted pack source)`

This binds the actual source bytes under the marketplace's declared canonical archive/fingerprint procedure.

### 3.3 Toolchain-relative identity

`id_V(P) = (id_S(P), ggen version, validator identities)`

Two identical packs executed by different compiler/validator versions are not automatically evidence-equivalent.

### 3.4 Qualification identity

`id_Q(P) = (id_V(P), fixture identities, environment class, qualification policy)`

This is the level at which replay receipts become reusable evidence.

The algebra MUST NOT silently substitute a weaker identity for a stronger one when deciding receipt reuse.

## 4. Semantic union

Let `G_P` and `G_Q` be RDF graphs. Since an RDF graph is a set of triples, ordinary graph union is:

`G_P ⊔ G_Q = G_P ∪ G_Q`.

Set union is associative, commutative, and idempotent. Those properties are useful but do not imply that the **meaning** of the union is admissible. Constraints, disjoint classes, closed-world expectations, target-specific invariants, or local vocabulary contracts can make a syntactically valid union unacceptable.

Therefore define an admission predicate:

`Compat_G(P,Q,G_P ∪ G_Q)`.

The semantic union exists for composition only when this predicate is satisfied.

### 4.1 Open-world versus manufacturing-world semantics

RDF itself uses open-world semantics: absence of a triple does not generally imply falsity. Manufacturing contracts often require local closed-world constraints: a chapter must have exactly one path; a pack name must match its directory; an output path must have exactly one owner.

The architecture therefore distinguishes:

- **knowledge semantics** — what the RDF graph says;
- **admission semantics** — what must be present or absent for manufacture;
- **projection semantics** — what selected facts become artifacts.

SHACL, native gates, or equivalent validators belong to the admission layer, not to RDF's base semantics.

## 5. Output ownership

For each pack define its target relation:

`τ_P : T_P → PathPattern`.

Two packs conflict structurally when their targets overlap and no explicit composition rule resolves the overlap.

Define:

`Conflict_path(P,Q) ⇔ ∃ p . p ∈ targets(P) ∩ targets(Q)`

unless the shared path has an admitted merge operator.

### 5.1 Default law: single writer

The safest default is:

`∀ path . |owners(path)| ≤ 1`.

This prevents “last writer wins” from becoming accidental semantics.

### 5.2 Admitted multi-writer paths

A multi-writer path is permitted only when a named deterministic operator exists, for example:

- set union with canonical ordering;
- keyed map merge with collision refusal;
- ordered concatenation with explicit precedence;
- AST merge with typed conflict handling.

The merge operator becomes part of the subject and therefore part of replay identity.

## 6. Query and template namespaces

Queries and templates are referenced by names in many generator systems. Composition without scoping can make those names ambient global state.

Define scoped identifiers:

`qid = pack-id :: query-name`

`tid = pack-id :: template-name`.

A composition implementation MAY expose local aliases, but the canonical identity should remain scoped. This allows two packs to use a local query called `rows` without accidental collision.

## 7. Dependency graph

Let marketplace dependencies form directed graph:

`D = (Packs, E_D)`

where edge `P → Q` means P requires Q's admitted semantic or manufacturing contract.

### 7.1 Dependency acyclicity

Acyclicity is sufficient for simple topological manufacture but not logically necessary for all semantic systems. Mutually recursive definitions could be meaningful if they converge to a fixed point.

The marketplace should therefore distinguish:

- **construction dependency** — must be resolved before projection;
- **semantic reference** — may be cyclic in graph knowledge;
- **qualification dependency** — receipt for one subject depends on evidence from another;
- **actuation dependency** — one authorized transition requires consequence of another.

Collapsing these edges into one generic dependency relation loses operational information.

### 7.2 Strongly connected components

If execution dependencies form a cycle, the component requires either:

1. a fixed-point semantics with proven convergence;
2. a staged bootstrap protocol;
3. a refusal.

“Run until it works” is not an admissible cycle semantics.

## 8. Authority composition

Let `Ω(P)` contain required capabilities and prohibitions. Authority is not ordinary data and MUST NOT compose by unconstrained union.

Define a policy-governed partial join:

`Ω_P ⊔_π Ω_Q ⇀ Ω_PQ`

where `π` is the governing authority policy.

The join may refuse because:

- combined permissions exceed an allowed ceiling;
- one pack requires a capability another explicitly forbids;
- a capability is legal only in a later `DO` phase;
- the composed subject crosses an isolation boundary;
- the authority principal is not valid for both subjects.

### Authority non-escalation invariant

For a composition admitted for construction only:

`capabilities(P ⊗ Q) ⊆ construction_ceiling`.

Deployment, merge, publication, remote mutation, or secret-bearing capabilities remain outside the constructor unless explicitly admitted by a distinct actuation contract.

## 9. Partial composition operator

Define pack composition:

`⊗ : Pack × Pack ⇀ Pack`.

`P ⊗ Q` is defined only if all required compatibility predicates hold:

`Compat(P,Q) =`

`Compat_identity ∧`

`Compat_graph ∧`

`Compat_targets ∧`

`Compat_queries ∧`

`Compat_dependencies ∧`

`Compat_toolchain ∧`

`Compat_authority`.

When defined:

`P ⊗ Q = (`

`  ι_PQ,`

`  admit(G_P ∪ G_Q),`

`  scope(Q_P ∪ Q_Q),`

`  T_P ⊎ T_Q,`

`  K_P ∧ K_Q ∧ K_cross,`

`  F_P ∪ F_Q ∪ F_cross,`

`  D_P ∪ D_Q ∪ {(P,Q) relations},`

`  Ω_P ⊔_π Ω_Q`

`)`.

`K_cross` and `F_cross` matter. Two packs that are independently valid can interact badly. Composition therefore requires cross-pack gates or fixtures whenever the overlap is semantically consequential.

## 10. Identity element

Define empty pack `ε` with:

- empty semantic contribution;
- no queries;
- no templates;
- no gates beyond `true`;
- no dependencies;
- no authority requirements;
- no outputs.

Then, under normalization:

`P ⊗ ε ≡ P`

`ε ⊗ P ≡ P`.

This identity is useful in planning and fold-based composition. It is not necessarily useful as a distributable marketplace pack.

## 11. Associativity

### Theorem 11.1 — Conditional associativity

If:

1. semantic unions remain admitted under either grouping;
2. target merge operators are associative;
3. query/template scoping is grouping-independent;
4. dependency normalization is grouping-independent;
5. cross-gates represent the same global predicates;
6. authority join `⊔_π` is associative for the participating capability sets;

then:

`(P ⊗ Q) ⊗ R ≡ P ⊗ (Q ⊗ R)`.

This is powerful because it permits parallel construction and tree-shaped composition. But the theorem is conditional. Any non-associative target merge or authority policy invalidates the optimization.

## 12. Commutativity

Composition is **not generally commutative**.

Reasons include:

- precedence-sensitive projection;
- dependency direction;
- ordered target merge;
- authority policy;
- cross-gate asymmetry;
- explicit extension/supersession semantics.

A pair may be proven independent, yielding local commutativity:

`Independent(P,Q) ⇒ P ⊗ Q ≡ Q ⊗ P`.

This becomes a useful scheduler optimization: independent packs can qualify or manufacture concurrently.

## 13. Idempotence

Semantic graph union is idempotent:

`G ∪ G = G`.

Pack composition is idempotent only for normalized pack identity and pure manufacture:

`P ⊗ P ≡ P`

requires that duplicate identity is collapsed rather than treated as two writers, and that no projection depends on application count or mutable state.

The marketplace SHOULD reject accidental duplicate pack instances rather than relying on idempotence unless duplicate semantics are explicit.

## 14. Refinement and substitutability

Define refinement relation:

`P' ⪯ P`

meaning P' may substitute for P for a declared consumer contract without invalidating the consumer's required semantics, targets, or authority ceiling.

A refinement proof may require:

- all required vocabulary terms preserved;
- query result schema compatible;
- generated artifact contract compatible;
- refusal behavior no weaker for safety constraints;
- authority requirements no greater;
- qualification predicates at least as strong;
- version/toolchain policy satisfied.

Semantic version numbers can be treated as hints about expected refinement, but the version string itself is not proof of substitutability.

## 15. Supersession

Sometimes a pack intentionally replaces another rather than composing with it.

Define:

`P' ▷ P`

for **supersession** when P' claims responsibility for P's consumer contract.

Supersession requires a migration witness:

`M : consumers(P) → consumers(P')`

or an explicit statement of incompatible consumer classes.

This prevents “new pack exists” from being interpreted as evidence that old consumers are safely migrated.

## 16. Pack families and parameterization

A pack family can be modeled as:

`P(θ)`

where `θ` is an admitted parameter object or semantic graph fragment. Parameterization is preferable to cloning packs when variation is genuinely data rather than behavior.

A parameter MUST enter through declared semantic/configuration source. Environment variables, filesystem accidents, or hidden defaults that alter output are latent parameters and therefore defects in subject completeness.

## 17. Projection as a functor-like mapping

For an admitted subset of packs, it is useful to view manufacture as mapping from semantic objects and lawful composition to artifact objects and artifact composition:

`μ : C_pack → C_artifact`.

The desirable laws are analogous to functor laws:

`μ(ε) ≡ identity_artifact`

`μ(P ⊗ Q) ≡ μ(P) ⊙ μ(Q)`

where `⊙` is the admitted artifact composition operator.

This analogy is useful only when the artifact merge semantics are explicit. If two templates can overwrite one another implicitly, there is no trustworthy `⊙` to preserve.

## 18. Evidence algebra

Receipts compose differently from packs.

Let receipt `r_P` prove claim set `C_P` for exact subject `S_P`. Receipt composition:

`r_P ⊗_e r_Q`

is admissible only when:

- subject identities are compatible with the combined claim;
- evidence epochs overlap or are proven reusable;
- toolchain and policy identities satisfy the new claim;
- predecessor dependencies are closed;
- no required cross-pack predicate is missing.

Independent pack receipts are therefore insufficient to crown `P ⊗ Q` when cross-interaction is possible. The composition requires at least a cross-boundary witness.

### Minimal recomputation principle

When a pack changes, invalidate only receipts whose proof dependencies include a changed identity.

Let receipt dependency graph be `R`. For changed node set `Δ`, the required revalidation set is the forward closure:

`invalidate(Δ) = Reachable_R(Δ)`.

This is the basis for safe incremental qualification.

## 19. Conflict taxonomy

Composition refusals should be typed.

| Code family | Meaning |
|---|---|
| `REFUSED:PACK_IDENTITY_*` | incompatible or duplicated identity |
| `REFUSED:GRAPH_*` | semantic/admission conflict |
| `REFUSED:TARGET_*` | output ownership or merge conflict |
| `REFUSED:QUERY_*` | query name/result contract conflict |
| `REFUSED:DEPENDENCY_*` | unsatisfied/cyclic execution dependency |
| `REFUSED:TOOLCHAIN_*` | incompatible manufacturing runtime |
| `REFUSED:AUTHORITY_*` | capability conflict or escalation |
| `REFUSED:EVIDENCE_*` | missing or stale receipt closure |

Typed conflict is not merely nicer error reporting. It is part of the algebra because undefined composition should explain **which predicate made the partial operator undefined**.

## 20. Worked example: mdBook pack plus marketplace consumer

Let `P_m` be the generic mdBook pattern-language pack and `C_g` the ggen Marketplace book consumer.

`P_m` contributes:

- vocabulary describing books and navigation entries;
- selection queries;
- templates producing `book.toml` and `docs/SUMMARY.md`;
- qualification fixture.

`C_g` contributes:

- book identity;
- chapter facts;
- ordered positions;
- existing Markdown corpus;
- publication workflow.

The composition is asymmetric: the consumer depends on the pack, while the pack MUST remain generic.

The self-hosting property is:

`μ(P_m ⊗ C_g) = marketplace book control surfaces`.

The first failed Pages execution demonstrated why composition needs schema compatibility: generic pack qualification passed, but the real consumer configuration mixed two ggen schema markers. That was a **consumer-composition defect**, not a failure of `P_m` in isolation.

## 21. Research questions opened by the algebra

1. Can target ownership and merge operators be represented as RDF and checked before template execution?
2. Can SHACL express enough cross-pack graph compatibility to eliminate most procedural gates?
3. Which authority joins form a lattice, and where must composition remain policy-specific?
4. Can ggen derive an exact impact graph from SPARQL/template dependencies rather than conservatively requalifying whole packs?
5. Can a proof assistant establish associativity for a large admitted pack subset and emit executable test obligations for the remaining impure edges?
6. Can pack refinement be checked semantically enough to make version compatibility machine-derived rather than author-declared?
7. Can receipt closure become a content-addressed proof cache whose reuse is safe under exact dependency identities?

## 22. Constitution for composition

The marketplace should evolve toward the following laws:

1. **No implicit writer conflict.** Every output path has one writer or an admitted deterministic merge operator.
2. **No ambient namespace.** Query, template, and semantic identities are scoped.
3. **No authority by union.** Capability composition is policy-governed and phase-bounded.
4. **No evidence by adjacency.** Independent receipts do not imply cross-pack validity.
5. **No hidden parameter.** Every output-relevant input belongs to the exact manufacturing subject.
6. **No silent incompatibility.** Undefined composition returns a typed refusal.
7. **No global rebuild by habit.** Revalidation follows the receipt dependency closure, unless uncertainty forces a conservative expansion.

The practical payoff is substantial. Once packs form a disciplined partial algebra, the marketplace can move from “a directory of generators” to a **compiler ecosystem in which composition, evidence reuse, and authority are themselves computable objects**.
