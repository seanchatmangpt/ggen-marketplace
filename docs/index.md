# ggen Marketplace

**ggen Marketplace** is the canonical, reviewable corpus of reusable ggen pack source and an executable research reference for ontology-first deterministic software manufacture. Packs are treated as bounded semantic manufacturing contracts that can be admitted, projected, qualified with the real ggen runtime, replayed, composed under explicit law, and published with evidence bound to exact source identity.

The book has three complementary structures:

1. **Diátaxis operational documentation** — tutorials, how-to guides, reference, and explanation for actually using the marketplace.
2. **Research monograph** — formal model, architecture, authority, evidence, verification, self-hosting, theorem catalogue, prior-art positioning, benchmark method, pack algebra, economics, and defense dossier.
3. **Research appendices** — notation, a numbered normative constitution, a machine-oriented receipt schema, and primary-source bibliography.

The result is intentionally both operational and falsifiable: prose explains the constitution, semantic source generates the book control plane, repository courts exercise the implementation, and unresolved claims are recorded as proof or experiment debt rather than promoted to guarantees.

## The core model

The shortest statement of the architecture is:

`A = μ(O*)`

`O*` is admitted observation, `μ` is lawful manufacture, and `A` is a bounded consequence. Construction and consequential execution are not the same operation:

`SELECT → CONSTRUCT → DO`

A more complete evidence path is:

`OBSERVE → ADMIT → SELECT → CONSTRUCT → VERIFY → DO → RECEIPT → REPLAY → STANDING`.

The repository therefore distinguishes observation, admission, generation, execution, mutation, verification, refusal, blockage, unsupported boundaries, and external actuation. `ALIVE` is reserved for observed execution against the exact admitted subject across the exact boundary being claimed.

## Research monograph

The research sequence is designed to move from thesis to formal system to empirical falsification.

1. [Research program: deterministic semantic software manufacture](thesis/00-research-program.md) — thesis, research questions, contributions, method, scope, and falsifiers.
2. [Formal calculus of admitted manufacture](thesis/01-formal-calculus.md) — objects, morphisms, admission, `SELECT/CONSTRUCT/DO`, deterministic replay, standing, and receipts.
3. [Ontology and compiler architecture](thesis/02-ontology-compiler-architecture.md) — RDF as IR, SPARQL selection, public ontology reuse, projection levels, and compiler-correctness claims.
4. [Authority, receipts, and standing](thesis/03-authority-receipts-and-standing.md) — bounded receipt discipline, no ambient authority, exact-head law, scoped standing, temporal evidence, and receipt DAGs.
5. [Verification, security, and evaluation](thesis/04-verification-security-and-evaluation.md) — qualification courts, threat model, vacuity, determinism, Little's Law, evaluation protocol, and validity threats.
6. [Self-hosting case study, falsification program, and research agenda](thesis/05-self-hosting-case-study-and-research-agenda.md) — mdBook self-hosting experiment, negative controls, formal hypotheses, metrics, research program, and disconfirming evidence.
7. [Theorem catalogue and proof obligations](thesis/06-theorem-catalogue.md) — definitions, theorems, propositions, countermodels, proof-status taxonomy, and mechanization roadmap.
8. [Related work, intellectual lineage, and distinguishing claims](thesis/07-related-work.md) — RDF/SPARQL/SHACL/SKOS/PROV-O, reproducible builds, Nix, Git, in-toto, SLSA, OCEL, Diátaxis, mdBook, code generation, and probabilistic AI; explicitly separates inherited primitives from marketplace synthesis.
9. [Experimental methods and benchmark protocol](thesis/08-experimental-methods.md) — populations, baselines, R0–R5 reproducibility classes, negative controls, statistics, replication packages, and preregistration.
10. [Pack algebra and compositional semantics](thesis/09-pack-algebra.md) — partial composition, target ownership, authority joins, refinement, supersession, receipt invalidation, and conditional algebraic laws.
11. [Evidence economics, throughput, and coordination collapse](thesis/10-evidence-economics.md) — construction/evidence/actuation queues, proof WIP, semantic leverage, coordination state-space, exception economics, and phase-transition criteria.
12. [Defense dossier: claims, evidence, falsifiers, and proof debt](thesis/11-defense-dossier.md) — claim ledger T1–T12, current evidence, strongest falsifiers, unresolved obligations, committee questions, and publication criteria.

The monograph is not a parallel source tree. Its navigation is represented in `docs/book.ttl` and projected through the marketplace's own `mdbook-pattern-language-pack` into mdBook control files.

## Research appendices

- [Notation, glossary, and symbol table](thesis/appendices/A-notation.md) fixes the symbols and distinctions used throughout the book.
- [Normative constitution](thesis/appendices/B-normative-constitution.md) converts the architectural doctrine into numbered `GGM-*` requirements using BCP 14 requirement language.
- [Evidence and receipt schema](thesis/appendices/C-receipt-schema.md) specifies an interoperable candidate evidence object, receipt DAG, standing derivation, invalidation, and release capsule.
- [Bibliography and primary sources](thesis/appendices/D-bibliography.md) anchors standards/tool claims in primary specifications and explicitly records literature-review gaps rather than fabricating completeness.

## Tutorials — learning-oriented

Follow these when you want guided experience and a concrete result.

- [Build your first pack](tutorials/first-pack.md)
- [Consume a marketplace pack](tutorials/consume-a-pack.md)

## How-to guides — task-oriented

Use these when you already know what you want to accomplish.

- [Publish a pack](how-to/publish-a-pack.md)
- [Update a pack](how-to/update-a-pack.md)
- [Validate locally](how-to/validate-locally.md)
- [Qualify every pack with ggen](how-to/qualify-all-packs.md)
- [Consume a pack](how-to/consume-a-pack.md)
- [Migrate a pack](how-to/migrate-a-pack.md)

## Reference — information-oriented

Use these for exact contracts, commands, and evidence boundaries.

- [Repository layout](reference/repository-layout.md)
- [Pack contract](reference/pack-contract.md)
- [Catalog command](reference/catalog-command.md)
- [Validation contract](reference/validation-contract.md)
- [ggen qualification contract](reference/ggen-qualification-contract.md)
- [CI standing policy](reference/ci-standing-policy.md)
- [Provenance](reference/provenance.md)
- [Standing](reference/standing.md)

## Explanation — understanding-oriented

Read these for architecture, rationale, and tradeoffs.

- [Why a separate marketplace](explanation/why-a-separate-marketplace.md)
- [Source of truth](explanation/source-of-truth.md)
- [Pack lifecycle](explanation/pack-lifecycle.md)
- [Security and authority](explanation/security-and-authority.md)

## How to read evidence in this repository

A green syntax parser proves syntax. A green marketplace validator proves the repository contract it actually evaluates. A successful real-ggen qualification proves the pack's bounded manufacturing path for the exercised consumer. Replay proves an equivalence property under the declared subject/environment. A target compiler proves only the target contract it actually executed. A successful Pages deployment proves publication of the exact built artifact. These claims compose only when their subject identities, evidence epochs, dependencies, and boundaries compose.

The book's central discipline is therefore:

> **Inspection is not execution. A workflow is not a run. Replay is not correctness. Provenance is not authority. A generated artifact is not source authority. A checkpoint is not a crown.**

## Research status

The strongest implementation claims are designed to be executable. Broader economic and organizational claims are explicitly hypotheses until benchmark data exists. The [defense dossier](thesis/11-defense-dossier.md) is the shortest path to the current evidence ledger and outstanding proof debt.
