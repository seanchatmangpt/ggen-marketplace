# pack-maturity-pack

`pack-maturity-pack` supplies reusable **mechanical** evidence for Level-5 promotion while refusing to invent domain semantics.

It currently generates three kinds of proof infrastructure:

1. deterministic regeneration and fixed-point convergence (`l5p:cap03`, `l5p:cap04`);
2. generated receipt verification (`l5p:cap09`);
3. a Level-5 Diátaxis documentation contract covering Tutorials, How-to guides, Reference, and Explanation.

The Diátaxis layer is not a claim that documentation alone makes a pack Level 5. It is a correspondence surface: the composing pack still owns semantic authority, domain admission/negative witnesses, real consumer/runtime execution, authority fencing, composition/class closure, and whatever external evidence its claim requires.

Repository-level doctrine: [`docs/reference/level5-maturity-contract.md`](../../docs/reference/level5-maturity-contract.md).

## The 5 × 7 context

Level 5 is evaluated independently across seven dimensions:

```text
semantic source
admission
manufacture
execution
receipt/replay
authority fence
composition
```

This pack intentionally focuses on generic mechanics that can be reused without knowing the domain. A composing pack must close the missing domain-specific dimensions itself rather than inheriting a global maturity badge.

## Level-5 Diátaxis contract

The generated documentation tree is:

```text
docs/level5/
  tutorials/getting-started.md
  how-to/operate-safely.md
  reference/contract.md
  explanation/architecture.md
```

Each quadrant has a distinct proof obligation.

### Tutorials

Tutorials are learning journeys. At Level 5 they expose the real path from admitted source to generated consequence and verification. The generated tutorial requires prerequisites, admitted inputs, executable path, verification, receipt/replay, falsifiers, and rollback.

A tutorial is not ALIVE because commands appear in Markdown. The consumer must bind the documented path to a real exact-subject execution court.

### How-to guides

How-to guides solve bounded operational goals. At Level 5 they make consequence and authority explicit. The generated how-to requires goal, prerequisites, admitted inputs, procedure, expected consequence, verification, receipt/replay, falsifiers, rollback, and authority boundary.

Any step that could reach consequential `DO` must identify the admitted authority path. Presentation, generated text, planner output, semantic derivation, and hooks have no ambient execution authority.

### Reference

Reference is normative and should be projected from canonical semantic/configuration sources wherever practical. The generated reference requires authoritative semantic source, ontology/classes/properties, generated surfaces, gates/refusals, configuration, commands, receipts/replay, authority, dependencies, compatibility, and maturity standing.

Hand-maintaining a second copy of canonical facts is a drift risk. Prefer graph/query/ggen projection.

### Explanation

Explanation preserves the `why`: architecture, semantic authority, calculus, exclusions, Chesterton fences, falsifiers, extension points, authority model, receipt/replay model, and operationalization.

The expected order is:

```text
Preserve → Fence → Calculus → Exclusions → Falsifiers → Extensions → Operationalization
```

## Typed documentation refusals

The generated structural court uses typed refusal identifiers:

- `L5-DOC-001`: missing Diátaxis quadrant;
- `L5-DOC-002`: reference lacks semantic-authority declaration;
- `L5-DOC-003`: tutorial lacks executable-path obligation;
- `L5-DOC-004`: reference lacks generated-surface documentation;
- `L5-DOC-005`: refusal/falsifier surface undocumented;
- `L5-DOC-006`: consequential how-to lacks authority boundary;
- `L5-DOC-007`: tutorial lacks receipt/replay obligation;
- `L5-DOC-008`: reference lacks anti-duplication/canonical-source rule;
- `L5-DOC-009`: composition/dependency behavior undocumented;
- `L5-DOC-010`: explanation lacks exclusions/falsifiers/extensions.

These are structural documentation refusals. They do not replace domain execution.

## What this closes

The pack's observed generic mechanical coverage remains deliberately narrow:

- `l5p:cap03` deterministic regeneration;
- `l5p:cap04` fixed-point convergence;
- `l5p:cap09` generated receipt verification.

The Diátaxis layer adds a machine-checkable documentation shape and explicit correspondence obligations, but it does not silently claim additional domain capabilities.

## Composition and class closure

`pack-maturity-pack` is a reusable **kernel/capability** dependency, not an umbrella that should absorb every domain pack. It should be composed by many families while each family preserves its own ontology, gates, runtime courts, and authority semantics.

If several packs duplicate maturity/receipt/Diátaxis mechanics, consolidate those mechanics here rather than copying them. If they differ in domain semantics or execution worlds, keep those differences in the composing profiles/worlds.

See [`docs/reference/pack-classes.md`](../../docs/reference/pack-classes.md) and [`docs/explanation/class-closure-and-consolidation.md`](../../docs/explanation/class-closure-and-consolidation.md).

## Usage

Compose the pack in the consumer's `ggen.toml`:

```toml
[packs]
pack-maturity-pack = { path = "../../packs/pack-maturity-pack" }
```

Run normal generation and then execute the consumer's generated tests. A Level-5 promotion court should combine these mechanical checks with domain-specific source correspondence, positive/negative witnesses, native runtime behavior, authority boundary, receipt verification, replay, and composition checks.

## Standing rule

```text
DiataxisClosure = Tutorial ∧ HowTo ∧ Reference ∧ Explanation
L5DocALIVE = DiataxisClosure ∧ Correspondence ∧ Execution ∧ Replay
```

If ontology, generated behavior, documentation, receipts, or replay diverge, promotion fails closed. This pack manufactures infrastructure; it does not manufacture standing from absence.
