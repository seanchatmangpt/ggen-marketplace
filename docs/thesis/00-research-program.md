# Research program: deterministic semantic software manufacture

## Abstract

This monograph studies **ggen Marketplace** as a software-manufacturing system rather than as a directory of reusable templates. The central object is a bounded transformation from admitted knowledge to reviewable consequences. In its compact form:

`A = μ(O*)`

where `O*` is admitted observation, `μ` is a lawful manufacturing transformation, and `A` is a materialized artifact. The engineering claim is not that all software can be reduced to text generation. The stronger and more useful claim is that a large class of software construction can be represented as **ontology → query → template → artifact**, with explicit admission boundaries, deterministic replay, and evidence-bearing receipts around consequential execution.

The marketplace is therefore evaluated as a compiler/distribution plane for semantic manufacturing contracts. A pack is not merely a bundle of files. It is a bounded program whose source includes identity, ontology, templates, optional gates, qualification fixtures, and provenance. The marketplace itself adds another layer: it decides which packs are admissible, how they are cataloged, how they are qualified against a real ggen runtime, and which evidence is sufficient to assign standing.

The research problem is important because conventional AI-assisted development collapses observation, interpretation, construction, and actuation into one probabilistic interaction. That architecture is productive but epistemically weak: a fluent answer can be mistaken for an admitted fact; generated text can be mistaken for an executable program; a workflow definition can be mistaken for a successful run; and a successful run can be mistaken for durable standing. ggen Marketplace separates these transitions and makes each one independently inspectable.

## Thesis

The thesis defended here is:

> A semantic software marketplace becomes substantially more reproducible, auditable, and composable when source knowledge is represented as explicit graph facts, generation is treated as a deterministic compiler projection, admission is separated from execution authority, and standing is derived from replayable evidence rather than from the existence of source files or workflow metadata.

This thesis has five consequences.

1. **The graph is prior to the projection.** Generated files are consequences of admitted semantic source; they are not the canonical model when a richer graph exists.
2. **Construction is prior to actuation.** A system may manufacture many reversible candidates without granting them authority to execute.
3. **Evidence is typed.** Inspection, admission, generation, execution, verification, and publication are distinct observations and must not be conflated.
4. **Replay is part of the contract.** Deterministic manufacture is incomplete if the same admitted subject cannot be regenerated and compared.
5. **Self-hosting is a falsifier.** A documentation pack that cannot manufacture the marketplace's own book is weaker evidence than a pack that survives that real consumer boundary.

## Research questions

The monograph is organized around six research questions.

### RQ1 — Representation

What is the smallest semantic representation that preserves the information required to manufacture a software artifact without embedding the artifact itself as canonical source?

The working answer is an RDF graph containing the relevant domain objects, relationships, ordering constraints, configuration facts, and provenance. Public vocabularies are preferred where their semantics fit; local terms exist only for irreducible domain concepts. This minimizes private ontology surface while preserving a graph suitable for SPARQL selection and deterministic projection.

### RQ2 — Admission

How can raw observation be distinguished from facts permitted to influence manufacture?

The system treats raw input as `O` and admitted input as `O*`. Admission is a typed transition, not a rhetorical assertion. Depending on the subject, admission may include structural validation, schema checks, provenance checks, policy constraints, or an external certifier. Failure to admit is not equivalent to refusal to execute: unsupported, malformed, unauthorized, and disproven subjects are different states.

### RQ3 — Manufacture

Under what conditions is generation a compiler operation rather than an unconstrained synthesis operation?

A manufacturing function is compiler-like when selection is explicit, templates are bounded, output paths are declared, source facts are inspectable, and replay over the same admitted subject converges. ggen's ontology/query/template pipeline makes those conditions operational. The important property is not the absence of sophisticated reasoning upstream; it is the absence of hidden ambient authority in the manufacturing edge itself.

### RQ4 — Authority

How can a system construct artifacts aggressively without allowing construction to become accidental execution?

The answer is a three-way separation:

`SELECT → CONSTRUCT → DO`

Selection identifies lawful candidates. Construction materializes reversible consequences. `DO` is the consequential boundary and therefore requires its own authority and receipt discipline. This separation permits combinatorial exploration without turning every generated possibility into an external side effect.

### RQ5 — Evidence

What evidence is sufficient to say that a pack, workflow, or marketplace is alive?

The answer depends on the claimed boundary. Reading a pack is inspection. Parsing its files is structural verification. Running ggen against an isolated consumer is manufacture. Running twice and obtaining the same consequence is replay evidence. Publishing a site is actuation. An `ALIVE` claim must name the subject, the executed boundary, the validator, and the result. A narrower successful boundary cannot silently crown a broader claim.

### RQ6 — Composition

Can semantic manufacturing packs compose without creating an unbounded dependency or authority graph?

Composition is tractable when dependency edges are explicit, paths are bounded, provenance remains recoverable, and each pack's execution surface remains constrained. A failed dependency edge is topology information, not proof that the whole graph is unusable. This leads to a graph-first approach to qualification and release rather than a monolithic pass/fail interpretation.

## Contributions

This work makes six engineering contributions.

### C1 — A source hierarchy

The repository defines a normative source hierarchy: marketplace policy, pack identity, ontology, templates, optional gates, generation contracts, and generated consumer consequences. The hierarchy prevents duplicate catalogs and clarifies where a change belongs.

### C2 — A standing model

The project uses evidence-bounded standing rather than binary confidence language. The useful lattice for repository work is:

- `UNKNOWN` — no sufficient observation.
- `PARTIAL_ALIVE` — one or more required boundaries have executed successfully, but the full claim has not.
- `ALIVE` — the exact admitted subject executed successfully across the claimed boundary.
- `BLOCKED` — execution was prevented by an external or missing prerequisite.
- `BUILD_BROKEN` — the subject reached an execution boundary and failed there.
- `UNSUPPORTED` — the requested boundary is outside the available capability contract.
- typed `REFUSED:*` — the system intentionally rejected the subject for a named reason.

The value of the model is not vocabulary; it is prevention of category errors.

### C3 — Marketplace qualification as an executable court

Marketplace CI does more than lint. It admits marketplace configuration, validates the corpus, proves deterministic catalog/archive projections, installs an admitted ggen binary, and executes pack qualification in isolated consumers. Qualification runs generation twice and rejects nondeterministic replay or mutation of pack source. This moves evidence from metadata toward observed behavior.

### C4 — Ontology-first documentation

The mdBook pattern-language pack demonstrates that documentation navigation can itself be manufactured from RDF. `book.toml` and `SUMMARY.md` are projections. Markdown chapters remain prose source. The book therefore does not require a hand-maintained second navigation catalog.

### C5 — Self-hosting as an integration experiment

The marketplace consumes the mdBook pack that it distributes. This is intentionally stronger than a toy example: the pack must operate inside the repository's actual source hierarchy and publication workflow. A self-hosting failure exposes real schema, path, qualification, and deployment assumptions.

### C6 — Falsifiable architecture

Each architectural claim is paired with a possible counterexample. If a pack cannot replay deterministically, determinism is false for that subject. If an output can execute without crossing the authority boundary, the construction/actuation separation is false. If a catalog requires duplicate manually synchronized metadata, source-of-truth claims are false. If the exact-head workflow runs a different commit, CI evidence is inadmissible for the claimed subject.

## Method

The work uses a design-science method with executable artifacts as the principal evidence. The unit of analysis is a transition in the manufacturing pipeline. For each transition we ask:

1. What is the input object?
2. What admits it?
3. Which transformation is authorized?
4. What consequence is produced?
5. What observable evidence binds consequence to subject?
6. Can the transition be replayed?
7. What falsifier would disprove the claim?

This gives a repeatable frame:

`parse → route → admit/refuse → construct → actuate → receipt → replay → standing`

The method intentionally avoids treating prose architecture as proof. Documentation specifies the intended constitution; executable validation shows which portion of that constitution has observed standing.

## Scope and exclusions

The marketplace is not presented as a proof that every software behavior should be encoded in RDF, nor that templates replace general-purpose programming languages. It also does not claim that determinism eliminates defects. A deterministic compiler can reproducibly generate the wrong program. The contribution is therefore **bounded determinism with explicit evidence**, not infallibility.

Likewise, qualification does not execute arbitrary pack-owned runtime programs. The repository's qualification court is deliberately filesystem-oriented: it proves that ggen can load a pack, manufacture consequences, converge on replay, and preserve source. Runtime semantics require a separate validator appropriate to the generated system.

This distinction is essential. A marketplace can assign standing to a pack's manufacturing contract without claiming that every possible generated application is correct.

## Reading strategy

The existing documentation remains organized by Diátaxis:

- **Tutorials** teach pack use.
- **How-to guides** solve concrete tasks.
- **Reference** defines exact contracts.
- **Explanation** gives operational rationale.

The dissertation chapters add a fifth reading mode: **research synthesis**. They connect those operational documents into a formal model, state invariants, identify falsifiers, and derive system-level consequences. Readers interested in implementation can move between the dissertation and the exact reference contracts rather than treating either alone as complete.

The next chapter defines the calculus used throughout the book.