# Explanation: pack lifecycle

A pack does not move directly from "files exist" to "production ready." Its lifecycle crosses distinct semantic, manufacturing, evidence, and authority transitions.

## Preserve

The lifecycle preserves the separation between source authority, admission, manufacture, verification, actuation, receipts, and standing. Collapsing these stages produces the most common category errors: treating a validator as a runtime test, a generated deployment as deployed infrastructure, or a green historical run as current standing.

## Lifecycle calculus

A mature pack moves through:

1. **Observe/author** — establish pack identity, semantic source, intended generated targets, dependencies, and authority ceiling.
2. **Admit** — validate manifest/RDF/path/gate/config constraints and refuse inadmissible subjects.
3. **Classify/compose** — identify kernel/capability/profile/world/compatibility/evidence/release-control responsibility and resolve composition conflicts.
4. **Manufacture** — run ggen against admitted source/consumer facts to produce bounded consequences.
5. **Replay** — rerun unchanged admitted inputs and establish fixed-point/deterministic consequence where claimed.
6. **Verify** — execute the native consumer/runtime court that actually proves the intended behavior.
7. **Actuate (optional)** — cross DO only through the consumer/runtime authority path responsible for consequential effect.
8. **Receipt** — bind identities, authority, consequence, execution evidence, replay, and standing.
9. **Document** — maintain Tutorial/How-to/Reference/Explanation correspondence to the same contract.
10. **Promote** — derive scoped standing from observed exact-subject evidence.
11. **Evolve/consolidate** — factor duplicated truth, add capabilities/profiles, or preserve compatibility while keeping class boundaries explicit.
12. **Deprecate/supersede** — name successor/migration path and retain compatibility until consumer migration is evidenced.

A compact form is:

```text
OBSERVE → ADMIT → COMPOSE → CONSTRUCT → VERIFY → [DO] → RECEIPT → REPLAY → STANDING
```

`DO` is optional; many marketplace packs lawfully stop at construction.

## Failure routing

The lifecycle makes defects easier to route:

- manifest/RDF/path/config failure → admission source;
- SPARQL/query/template/project rendering failure → manufacture source;
- second-pass drift → determinism/replay source;
- compiled/service/protocol behavior failure → consumer/runtime boundary;
- missing authority → `BLOCKED` at DO, not a reason to fake execution;
- stale/missing docs → Diátaxis correspondence;
- duplicate class truth/target ownership → composition/consolidation;
- valid legacy consumer with newer successor → compatibility/migration.

Do not repair a downstream symptom by bypassing its upstream owning transition.

## Level-5 lifecycle

Level 5 is reached only when the dimensions claimed in [the 5 × 7 maturity contract](../reference/level5-maturity-contract.md) close over this lifecycle. `pack-maturity-pack` can make regeneration/receipt/Diátaxis mechanics reusable, but the domain pack still owns domain admission, negative witnesses, runtime verification, authority, and composition.

## Requalification

Any material change to semantic source, gate, template, toolchain, admitted config, dependency, generated contract, runtime, authority policy, or relevant documentation can invalidate predecessor evidence. Re-run the narrowest owning court first, then expand to the complete affected closure.

Historical evidence may be reused only after identity/equivalence has been proved; it is never transferred because the pack name stayed the same.

## Consolidation and deprecation

As a family matures, its lifecycle should move duplicated semantic authority upward into kernels/capability modules and move product/environment-specific facts downward into profiles/worlds.

Deprecation is not deletion — but staleness can be. A CompatibilityPack should name its successor and retained seam until the consumer graph demonstrates that removal is safe. Separately, packs that go stale (no updates within the freshness window) may still be deleted outright by the staleness deletion court, after conservation checks confirm no consumer is left behind (see below).

Lifecycle decisions are recorded in the repository's lifecycle registry (`lifecycle.toml`) on two independent axes. **State** (`active`, `deprecated`, `superseded`, `retired`) says what a pack is now and what consumers should do. **Intent** (`consolidate`, `upgrade`, `replace`, `review`, `keep-separate`) says what we plan, and is advisory. Keeping them apart lets a review lead be recorded without pretending it is a deprecation, and lets a ruled-out overlap be recorded (`keep-separate`) so the next audit does not re-derive it. The registry lives beside `pack.toml` rather than in it because the real ggen loader refuses unknown `[pack]` keys. See [the registry reference](../reference/pack-lifecycle-registry.md) and [How to flag a pack's lifecycle](../how-to/flag-a-pack-lifecycle.md).

See [Class closure and consolidation](class-closure-and-consolidation.md).

## Staleness deletion court

Deprecation keeps a pack on disk; staleness does not. Under the 7d-staleness deletion policy, a pack directory that has not been updated within 7 days (cutoff 2026-09-24) is eligible for deletion — but only after a conservation court verifies zero consumer references, zero cross-pack references, and no front-door status. The court ran on 2026-10-01 (commit `ee6008a41`), deleting 68 pack directories in one pass.

Deletion by the court is not loss: every deleted pack remains recoverable from git history at `ee6008a41^` (see [the retired-packs ledger](../reference/retired-packs-26.10.01.md)).
