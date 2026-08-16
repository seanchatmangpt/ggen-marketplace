# ggen Marketplace

**ggen Marketplace** is the canonical, reviewable corpus of reusable ggen pack source: ontology-backed software manufacturing contracts that can be admitted, projected, qualified with the real ggen runtime, replayed, and published with evidence bound to exact source identity.

The documentation has two complementary structures.

The first is **Diátaxis**, which keeps operational documentation separated by reader need. The second is a **research monograph**, which treats the marketplace as a deterministic semantic software-manufacturing system and develops its formal model, evidence theory, security boundaries, economics, and falsification program.

## The core model

The shortest statement of the architecture is:

`A = μ(O*)`

`O*` is admitted observation, `μ` is lawful manufacture, and `A` is a bounded consequence. Construction and consequential execution are not the same operation:

`SELECT → CONSTRUCT → DO`

The repository's evidence model therefore distinguishes observation, admission, execution, mutation, verification, refusal, blockage, and unsupported boundaries. `ALIVE` is reserved for observed execution against the exact admitted subject across the exact boundary being claimed.

## Research monograph

Start here for the dissertation-level treatment.

1. [Research program: deterministic semantic software manufacture](thesis/00-research-program.md) — thesis, research questions, contributions, method, scope, and falsifiers.
2. [Formal calculus of admitted manufacture](thesis/01-formal-calculus.md) — objects, morphisms, admission, `SELECT/CONSTRUCT/DO`, deterministic replay, standing, and receipts.
3. [Ontology and compiler architecture](thesis/02-ontology-compiler-architecture.md) — RDF as IR, SPARQL selection, public ontology reuse, pack algebra, projection levels, and compiler correctness claims.
4. [Authority, receipts, and standing](thesis/03-authority-receipts-and-standing.md) — BRCE, no ambient authority, exact-head law, scoped standing, temporal evidence, and receipt DAGs.
5. [Verification, security, and evaluation](thesis/04-verification-security-and-evaluation.md) — qualification capsules, threat model, vacuity, determinism, Little's Law, evaluation protocol, and validity threats.
6. [Self-hosting case study and research agenda](thesis/05-self-hosting-case-study-and-research-agenda.md) — mdBook self-hosting experiment, negative controls, formal hypotheses, metrics, research program, and disconfirming evidence.

The monograph is not a parallel source tree. Its navigation is represented in `docs/book.ttl` and projected through the marketplace's own `mdbook-pattern-language-pack` into mdBook control files.

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

A green syntax parser proves syntax. A green marketplace validator proves the repository contract. A successful real-ggen qualification proves the pack's bounded manufacturing path for the exercised consumer. A target runtime test proves only the behavior it actually executed. A successful Pages deployment proves publication of the exact built artifact. These claims compose only when subject identities and boundaries compose.

That distinction is the book's central discipline: **inspection is not execution, workflow is not run, generated artifact is not authority, and a checkpoint is not a crown.**
