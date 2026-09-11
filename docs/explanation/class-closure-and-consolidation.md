# Explanation: class closure and consolidation

A mature marketplace can contain hundreds or thousands of pack instances without containing hundreds or thousands of independent semantic authorities. The consolidation problem is therefore not directory count. It is **authority duplication**.

The target is class closure:

```text
canonical kernel/class semantics
        ↓
orthogonal reusable capabilities
        ↓
umbrella composition / explicit defaults
        ↓
parameterized profiles and domain worlds
```

## Preserve

Before consolidating anything, preserve each pack's real contracts: semantic facts, generated targets, consumers, qualification fixtures, negative witnesses, runtime dependencies, compatibility seams, authority ceiling, and provenance.

Similar names are not evidence of equivalence. A Terraform profile and a generic deployment calculus may share vocabulary while owning different responsibilities. Two Gym worlds may share a world schema while representing non-equivalent environments. A legacy pack may intentionally preserve a broken-looking API because real consumers still depend on it.

## Fence

The consolidation fence is:

```text
duplicate truth → consolidate
independent domain semantics → preserve
shared protocol vocabulary → canonicalize
independent runtime implementation → preserve
compatibility seam → preserve until migration is proven
similar directory shape → insufficient evidence
```

Deletion is irreversible relative to consumers. Therefore the burden of proof is on equivalence/supersession, not on preservation.

## Calculus

For packs `P` and `Q`, consolidation is lawful only after classifying at least:

- `S(P), S(Q)` — semantic authority sets;
- `G(P), G(Q)` — generated target ownership;
- `A(P), A(Q)` — admission/refusal law;
- `X(P), X(Q)` — execution/runtime boundary;
- `R(P), R(Q)` — receipt/replay requirements;
- `Auth(P), Auth(Q)` — authority ceilings;
- `C(P), C(Q)` — consumer/compatibility obligations.

Useful outcomes are not limited to physical merge:

1. **Canonicalize shared vocabulary** — move duplicated protocol/class semantics into one kernel while keeping implementations separate.
2. **Factor capability modules** — extract orthogonal behavior used by several siblings.
3. **Create an umbrella** — give normal consumers one stable dependency while retaining modules for advanced composition.
4. **Convert products to profiles** — keep domain ABox/defaults small over a shared projection engine.
5. **Deprecate compatibility-only packs** — name successors while preserving old seams until consumers migrate.
6. **Retain separate worlds/runtimes** — when equivalence cannot be proved or merging would change the evaluated system.

## High-value marketplace families

The recurring consolidation opportunities are structural:

- UI/shadcn/deck.gl/react packs should share a reversible UI projection grammar while preserving product-specific domain facts;
- repository lifecycle packs should share one state/morphism calculus rather than copy `as-found → intervention → reconciliation` semantics;
- release/publish packs should share one release lifecycle and authority model;
- enterprise/Fortune-5 architecture packs should share architecture/TOGAF vocabulary with organization/product profiles layered above it;
- MCP implementation packs should share canonical protocol semantics while retaining different runtimes;
- TCPS and wasm4pm families should expose stable umbrellas over orthogonal modules;
- assurance/reconstitution packs should share evidence/standing mathematics while preserving distinct courts and subjects.

These are hypotheses until pairwise source/consumer comparison proves the proposed boundary. Consolidation work should make the hypothesis executable rather than treating the family name as proof.

## Exclusions

Do not consolidate by copying files into a larger mega-pack. That merely centralizes duplication.

Do not make an umbrella the new semantic authority for facts already owned by modules. An umbrella should primarily declare composition/defaults.

Do not collapse compatibility history before consumers have an admitted migration path.

Do not collapse executable worlds solely because they reuse the same public ontology.

## Falsifiers

A proposed consolidation is falsified or must be narrowed when:

- consumers require incompatible semantic definitions;
- generated targets conflict under composition;
- negative witnesses differ in a way that changes accepted behavior;
- authority joins become wider after consolidation;
- a legacy seam has active consumers without a successor mapping;
- runtime/toolchain requirements cannot be jointly satisfied;
- one pack's evidence court is incorrectly promoted to authority over another subsystem.

One failed edge is topology, not graph failure: retain the independent branch and continue factoring whatever equivalence is actually proved.

## Extensions

As families mature, encode class membership, supersession, umbrella membership, capability dependencies, compatibility obligations, and target ownership in RDF so consolidation becomes graph analysis instead of naming heuristics.

A future marketplace court should be able to report:

```text
DUPLICATE_SEMANTIC_AUTHORITY
TARGET_OWNERSHIP_CONFLICT
ORPHAN_PROFILE
UMBRELLA_CYCLE
LEGACY_WITHOUT_SUCCESSOR
SUCCESSOR_WITH_UNMIGRATED_CONSUMER
CLASS_WITHOUT_CANONICAL_KERNEL
```

without automatically deleting anything.

## Operationalization

Use [pack classes](../reference/pack-classes.md) to classify the family, then follow [How to consolidate a pack family](../how-to/consolidate-a-pack-family.md). Publish consolidation as a dependency-closed migration with exact before/after identities, compatibility evidence, negative controls, rollback, and scoped standing.
