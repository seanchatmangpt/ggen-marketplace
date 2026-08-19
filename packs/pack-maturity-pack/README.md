# pack-maturity-pack

`pack-maturity-pack` supplies reusable mechanical evidence for Level-5 promotion while refusing to invent domain semantics.

It currently generates three kinds of proof infrastructure:

1. deterministic regeneration and fixed-point convergence (`l5p:cap03`, `l5p:cap04`);
2. generated receipt verification (`l5p:cap09`);
3. a Level-5 Diátaxis documentation contract covering Tutorials, How-to guides, Reference, and Explanation.

The Diátaxis layer is not a claim that documentation alone makes a pack Level 5. It is a correspondence surface: the consuming pack must still supply and execute its own semantic source, domain behavior, positive and negative witnesses, consequential boundary, and runtime evidence.

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

Tutorials are learning journeys. At Level 5 they must expose the real path from admitted source to generated consequence and verification. The generated tutorial therefore requires explicit sections for prerequisites, admitted inputs, executable path, verification, receipt/replay, falsifiers, and rollback.

A tutorial is not ALIVE because commands are printed in Markdown. The composing consumer must bind the documented path to a real exact-subject execution court.

### How-to guides

How-to guides solve bounded operational goals. At Level 5 they must make consequence and authority explicit. The generated how-to requires goal, prerequisites, admitted inputs, procedure, expected consequence, verification, receipt/replay, falsifiers, rollback, and authority boundary.

Any step that could reach consequential `DO` must identify the admitted authority path. Presentation, generated text, planner output, semantic derivation, or hooks have no ambient execution authority.

### Reference

Reference is normative and should be projected from canonical semantic sources wherever possible. The generated reference requires authoritative semantic source, ontology/classes/properties, generated surfaces, gates/refusals, configuration, commands, receipts/replay, authority, dependencies, compatibility, and maturity standing.

Hand-maintaining a second copy of canonical facts is a drift risk. Prefer graph/query/ggen projection.

### Explanation

Explanation preserves the `why`: architecture, semantic authority, calculus, exclusions, Chesterton fences, falsifiers, extension points, authority model, receipt/replay model, and operationalization.

The expected explanatory order is:

```text
Preserve -> Fence -> Calculus -> Exclusions -> Falsifiers -> Extensions -> Operationalization
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

These are structural refusals. They do not replace domain execution.

## What this closes

The pack's observed mechanical coverage remains deliberately narrow:

- `l5p:cap03` deterministic regeneration;
- `l5p:cap04` fixed-point convergence;
- `l5p:cap09` generated receipt verification.

The Level-5 Diátaxis layer adds a machine-checkable documentation shape and explicit correspondence obligations, but it does not silently claim additional upstream `l5p:` capabilities unless those capabilities are defined and executed by the consumer.

## Usage

Compose the pack in the consumer's `ggen.toml`:

```toml
[packs]
pack-maturity-pack = { path = "../../packs/pack-maturity-pack" }
```

Run normal generation and then execute the consumer's generated tests. A Level-5 promotion court should combine these mechanical checks with the consumer's domain-specific source correspondence, positive and negative witnesses, runtime behavior, authority boundary, receipt verification, and replay.

## Standing rule

A complete Level-5 documentation claim requires all four quadrants plus correspondence and execution evidence:

```text
DiataxisClosure = Tutorial ∧ HowTo ∧ Reference ∧ Explanation
L5DocALIVE = DiataxisClosure ∧ Correspondence ∧ Execution ∧ Replay
```

If ontology, generated behavior, documentation, receipts, or replay diverge, promotion must fail closed rather than rounding documentation up to standing.
