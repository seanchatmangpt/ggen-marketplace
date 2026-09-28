# ggen Marketplace

**ggen Marketplace** is the canonical, reviewable corpus of reusable ggen pack source and an executable reference for ontology-first deterministic software manufacture. Packs are bounded semantic manufacturing contracts: source is admitted, consequences are manufactured, real boundaries are executed, evidence is receipted/replayed, and standing is scoped to the exact subject that actually ran.

The documentation has four cooperating structures:

1. **Diátaxis operational documentation** — tutorials, how-to guides, reference, and explanation for using and evolving the marketplace.
2. **Level-5 promotion program** — the 5 × 7 maturity matrix, Diátaxis closure, pack classes, consolidation/class closure, and promotion evidence.
3. **Research monograph** — formal model, architecture, authority, evidence, verification, self-hosting, theorem catalogue, prior-art positioning, benchmark method, pack algebra, economics, defense dossier, and Level-5/class-closure formalization.
4. **Research appendices** — notation, normative constitution, receipt schema, and primary-source bibliography.

The result is intentionally operational and falsifiable: semantic source drives manufacturing/documentation control planes, exact-subject courts exercise implementation boundaries, and unresolved claims remain proof or experiment debt rather than silently becoming guarantees.

## Core model

The shortest statement is:

```text
A = μ(O*)
```

`O*` is admitted observation, `μ` is lawful manufacture, and `A` is a bounded consequence. Selection, construction, and consequential execution remain distinct:

```text
SELECT → CONSTRUCT → DO
```

A complete evidence path is:

```text
OBSERVE → ADMIT → SELECT → CONSTRUCT → VERIFY → DO → RECEIPT → REPLAY → STANDING
```

Not every pack reaches every transition. A documentation pack may stop at CONSTRUCT; a simulation may execute without external DO; a marketplace qualification court may prove deterministic manufacturing without executing the generated application. The claim must name the boundary.

## Level-5 promotion program

Level 5 is closure across seven dimensions, not a single scalar score:

1. semantic source;
2. admission;
3. manufacture;
4. execution;
5. receipt/replay;
6. authority fence;
7. composition.

The fifth maturity level is **class-closed**: authoritative semantics are canonicalized, invalid states are fail-closed, manufacture converges deterministically, the claimed runtime boundary has exact-subject evidence, receipts/replay bind consequence identity, DO has no ambient authority, and families compose through explicit kernels/capabilities/profiles instead of duplicated truth.

Documentation is a required closure surface:

```text
Tutorial ∧ How-to ∧ Reference ∧ Explanation
```

Use these documents as the Level-5 spine:

- [Tutorial: Level-5 promotion slice](tutorials/level5-promotion.md)
- [How to promote a pack to Level 5](how-to/promote-a-pack-to-level5.md)
- [Level-5 maturity contract](reference/level5-maturity-contract.md)
- [Why Level 5 requires Diátaxis](explanation/level5-diataxis.md)
- [Pack classes](reference/pack-classes.md)
- [How to consolidate a pack family](how-to/consolidate-a-pack-family.md)
- [Class closure and consolidation](explanation/class-closure-and-consolidation.md)
- [Research formalization: Level-5 maturity, Diátaxis correspondence, and class closure](thesis/12-level5-maturity-and-class-closure.md)

`pack-maturity-pack` supplies reusable mechanical regeneration/receipt/documentation infrastructure, but it deliberately cannot invent domain semantics, negative witnesses, consumer runtime success, external observations, or authority that the composing pack does not possess.

## Tutorials — learning-oriented

Follow these when you want guided experience and a concrete result.

- [Build your first pack](tutorials/first-pack.md)
- [Consume a marketplace pack](tutorials/consume-a-pack.md)
- [Take a pack through a Level-5 promotion slice](tutorials/level5-promotion.md)

## How-to guides — task-oriented

Use these when you already know the result you need.

- [Publish a pack](how-to/publish-a-pack.md)
- [Update a pack](how-to/update-a-pack.md)
- [Validate locally](how-to/validate-locally.md)
- [Qualify every pack with ggen](how-to/qualify-all-packs.md)
- [Consume a pack](how-to/consume-a-pack.md)
- [Migrate a pack](how-to/migrate-a-pack.md)
- [Promote a pack to Level 5](how-to/promote-a-pack-to-level5.md)
- [Consolidate a pack family](how-to/consolidate-a-pack-family.md)

## Reference — information-oriented

Use these for exact contracts, commands, evidence boundaries, and refusal law.

- [Repository layout](reference/repository-layout.md)
- [Pack contract](reference/pack-contract.md)
- [Pack classes](reference/pack-classes.md)
- [Level-5 maturity contract](reference/level5-maturity-contract.md)
- [Catalog command](reference/catalog-command.md)
- [Validation contract](reference/validation-contract.md)
- [ggen qualification contract](reference/ggen-qualification-contract.md)
- [CI standing policy](reference/ci-standing-policy.md)
- [Provenance](reference/provenance.md)
- [Standing](reference/standing.md)

## Explanation — understanding-oriented

Read these for architecture, rationale, fences, exclusions, and extension law.

- [Why a separate marketplace](explanation/why-a-separate-marketplace.md)
- [Source of truth](explanation/source-of-truth.md)
- [Pack lifecycle](explanation/pack-lifecycle.md)
- [Security and authority](explanation/security-and-authority.md)
- [Why Level 5 requires Diátaxis](explanation/level5-diataxis.md)
- [Class closure and consolidation](explanation/class-closure-and-consolidation.md)
- [ggen ecosystem map](explanation/ggen-ecosystem-map.md)

## Research monograph

The research sequence moves from thesis to formal system to empirical falsification and portfolio closure.

1. [Research program: deterministic semantic software manufacture](thesis/00-research-program.md)
2. [Formal calculus of admitted manufacture](thesis/01-formal-calculus.md)
3. [Ontology and compiler architecture](thesis/02-ontology-compiler-architecture.md)
4. [Authority, receipts, and standing](thesis/03-authority-receipts-and-standing.md)
5. [Verification, security, and evaluation](thesis/04-verification-security-and-evaluation.md)
6. [Self-hosting case study, falsification program, and research agenda](thesis/05-self-hosting-case-study-and-research-agenda.md)
7. [Theorem catalogue and proof obligations](thesis/06-theorem-catalogue.md)
8. [Related work, intellectual lineage, and distinguishing claims](thesis/07-related-work.md)
9. [Experimental methods and benchmark protocol](thesis/08-experimental-methods.md)
10. [Pack algebra and compositional semantics](thesis/09-pack-algebra.md)
11. [Evidence economics, throughput, and coordination collapse](thesis/10-evidence-economics.md)
12. [Defense dossier: claims, evidence, falsifiers, and proof debt](thesis/11-defense-dossier.md)
13. [Level-5 maturity, Diátaxis correspondence, and class closure](thesis/12-level5-maturity-and-class-closure.md)

The monograph is not a parallel source tree. Its navigation is represented in `docs/book.ttl` and projected through `mdbook-pattern-language-pack` during the Pages build.

## Research appendices

- [Notation, glossary, and symbol table](thesis/appendices/A-notation.md)
- [Normative constitution](thesis/appendices/B-normative-constitution.md)
- [Evidence and receipt schema](thesis/appendices/C-receipt-schema.md)
- [Bibliography and primary sources](thesis/appendices/D-bibliography.md)

## Evidence reading law

A syntax parser proves syntax. Marketplace validation proves the repository contract it executes. Real-ggen qualification proves bounded load/manufacture/replay for the admitted marketplace subject. A native consumer court proves only the runtime boundary it actually executes. Replay proves the declared equivalence property, not universal correctness. A successful Pages build proves that the exact semantic navigation/doc source can be manufactured into a book.

The central discipline is:

> **Inspection is not execution. A workflow is not a run. Replay is not correctness. Provenance is not authority. A generated artifact is not source authority. A checkpoint is not a crown.**

Standing therefore remains typed and scoped: `UNKNOWN`, `PARTIAL_ALIVE`, `ALIVE`, `BLOCKED`, `BUILD_BROKEN`, `UNSUPPORTED`, and typed `REFUSED:*` states. Historical success transfers only when subject, validator, toolchain, configuration, environment, and claimed boundary remain equivalent.
