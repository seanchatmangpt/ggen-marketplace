# Self-hosting case study, falsification program, and research agenda

## 1. Why self-hosting is a serious experiment

A reusable pack is easy to make look successful in a toy fixture. A carefully chosen consumer can omit awkward path layouts, version interactions, existing documentation, CI policy, and publication constraints. Self-hosting raises the standard: the marketplace uses the same mdBook pattern-language pack that it distributes to manufacture its own documentation control surfaces and then attempts to publish the resulting book.

The experiment is intentionally recursive:

`marketplace distributes pack`

`pack manufactures marketplace book`

`marketplace CI qualifies pack`

`Pages workflow manufactures book again`

`mdBook compiles the projection`

`Pages publishes the consequence`

This loop does not prove universal correctness. It does test whether the abstraction survives a real repository boundary with nontrivial existing documentation and independent CI governance.

## 2. Experimental subject

The subject consists of four source layers.

### 2.1 Generic pack source

`packs/mdbook-pattern-language-pack/`

The pack defines:

- an RDF vocabulary for books and ordered navigation entries;
- a SKOS pattern language explaining the design patterns;
- templates for `book.toml` and `SUMMARY.md`;
- a qualification fixture that exercises the generic projection.

### 2.2 Consumer semantic source

`docs/book.ttl`

This graph defines the actual ggen Marketplace book: title, source directory, build directory, repository identity, and ordered navigation over the existing Markdown corpus.

### 2.3 Existing prose source

`docs/`

Tutorials, how-to guides, reference, explanation, and this research monograph remain ordinary Markdown. The pack does not own or duplicate their prose.

### 2.4 Publication contract

The root consumer `ggen.toml` connects the book graph to the pack, and the Pages workflow runs the admitted ggen runtime before invoking mdBook.

These layers make source ownership explicit. The generic pack knows how to manufacture a book; the consumer graph says which book; the Markdown corpus says what the chapters mean; the workflow defines how the static consequence reaches publication.

## 3. Hypotheses

The self-hosting experiment tests six hypotheses.

### H1 — Genericity

The mdBook pack can manufacture a real consumer book without embedding marketplace-specific navigation in the generic pack.

### H2 — Source singularity

Book navigation can be maintained in RDF and projected into mdBook control files without a manually synchronized second navigation authority.

### H3 — Qualification validity

The marketplace qualification court can establish replay-convergent manufacture for the generic pack independently of the self-hosting consumer.

### H4 — Integration validity

The root consumer can use the admitted ggen runtime to manufacture the same control surfaces in the real repository.

### H5 — Compiler validity

The generated `book.toml` and `SUMMARY.md` are accepted by the pinned mdBook compiler.

### H6 — Publication validity

The compiled static artifact can cross the distinct GitHub Pages deployment boundary under explicit workflow authority.

The hypotheses are layered. Failure of H4 does not falsify H3; failure of H6 does not falsify H5.

## 4. First execution result

The first exact-head run produced a useful split result.

The marketplace CI workflow succeeded. The vacuity audit succeeded. These observations support the generic pack's admission and qualification claims for that exact commit.

The Pages workflow then reached the self-hosting manufacture step and failed before mdBook compilation. The admitted ggen runtime reported an ambiguous root `ggen.toml`: `project.version` marked a declarative project schema while the packs table represented a frontmatter-style pack consumer. ggen refused to guess between schemas.

This result is a **BUILD_BROKEN self-hosting consumer**, not a generic pack failure.

The distinction validates the evidence model itself. If the architecture had only one global “green/red” state, the successful qualification evidence would have been discarded or the publication failure would have been ignored. Boundary-scoped standing preserved both facts.

## 5. Root cause and repair

The root cause is a mixed-schema consumer configuration.

The lawful repair is minimal:

- preserve the frontmatter pack-reference shape;
- remove the declarative-only `project.version` marker;
- rerun `ggen sync run` on the exact new head;
- only after generation succeeds, allow mdBook compilation;
- only after compilation succeeds, allow Pages artifact upload/deployment.

This repair follows the transition-local debugging rule:

`preserve evidence → locate failed edge → repair narrowest cause → rerun edge → expand after success`

No weakening of qualification, no manual bypass of generated `SUMMARY.md`, and no direct deployment of prebuilt HTML is justified by the observed failure.

## 6. The book as an executable dissertation

This monograph is not separate from the engineering artifact. Its own navigation is part of `docs/book.ttl`; therefore adding these chapters changes the semantic consumer subject. The generated `SUMMARY.md` is expected to change mechanically.

This creates an unusual but useful property: the dissertation's table of contents is itself evidence of the compiler model it describes.

The layers are:

`research argument`

→ represented as Markdown chapters

`navigation intent`

→ represented as RDF facts

`book control surface`

→ manufactured by ggen

`static publication`

→ compiled by mdBook

`public consequence`

→ deployed by Pages

The content and the mechanism are therefore mutually testable. A broken navigation projection is not merely a documentation inconvenience; it is a failure of the architecture described by the book.

## 7. Negative controls

A PhD-level engineering claim needs experiments that are expected to fail.

The mdBook pack should eventually maintain explicit negative controls for at least these conditions.

### NC1 — Duplicate positions

Two navigation entries claim the same position when total ordering requires uniqueness.

Expected outcome: semantic admission refusal or deterministic tie-breaking explicitly defined by policy. Silent unstable ordering is unacceptable.

### NC2 — Chapter without path

A navigation entry is marked `chapter` but has no path.

Expected outcome: refusal before projection or an explicit schema constraint.

### NC3 — Heading with path

A heading carries a chapter path when the model defines headings as non-linking structural entries.

Expected outcome: either explicit support or refusal; implicit behavior is a model gap.

### NC4 — Path outside source directory

A chapter path escapes the configured mdBook source root.

Expected outcome: refusal.

### NC5 — Missing chapter file

The graph references a Markdown file absent from the consumer tree.

Expected outcome: the publication court fails before deployment; ideally an earlier semantic/filesystem gate localizes the error.

### NC6 — Nondeterministic order

The query omits `ORDER BY` while output ordering remains semantically important.

Expected outcome: a replay or dedicated query-contract test exposes instability.

### NC7 — Hand-edited generated navigation

`docs/SUMMARY.md` diverges from the graph/template consequence.

Expected outcome: regeneration produces a detectable diff or freeze/refusal policy identifies manual drift.

### NC8 — Exact-head mismatch

The workflow checks out a different SHA from the subject it claims to validate.

Expected outcome: typed refusal before manufacture.

These controls form a concrete future test program rather than a generic recommendation to “add more tests.”

## 8. Formal hypotheses for future proof

Several properties are candidates for stronger formalization.

### P1 — Navigation totality

For every admitted chapter entry `e`, exactly one path exists and the path resolves within the source root.

### P2 — Position uniqueness

For any two distinct admitted navigation entries `e1` and `e2`, `position(e1) ≠ position(e2)`.

### P3 — Projection determinism

For fixed admitted graph `G`, template set `T`, and ggen toolchain `v`:

`digest(μ_v(G,T))` is invariant under replay in the bounded qualification environment.

### P4 — Source non-mutation

Manufacture does not modify the admitted pack source subtree.

### P5 — Authority separation

No qualification transition can invoke Pages deployment authority.

### P6 — Exact-subject evidence

Every workflow receipt used to assign release standing references the exact commit SHA whose tree was executed.

Some of these properties are well suited to executable assertions; others could be encoded in SHACL or a theorem prover. The important design rule is to use the strongest mechanism that remains connected to the actual runtime boundary. A theorem about a model that is not linked to the executed subject is not a substitute for integration evidence.

## 9. Research agenda

### 9.1 SHACL admission for pack and consumer graphs

Today, many graph constraints are expressed procedurally or implicitly in templates. A next step is to define reusable SHACL shapes for pack ontologies and mdBook consumers. This would move errors such as missing paths or invalid kinds earlier in the evidence ladder.

Research question: how much validation can move into declarative graph shapes without duplicating semantics already enforced by ggen or target compilers?

### 9.2 Receipt ontology

Receipts should become first-class semantic objects. A receipt ontology could reuse PROV-O for activities/entities/agents and define marketplace-specific bindings for subject SHA, authority witness, validator, consequence digest, replay command, and standing.

Research question: can one receipt graph support both human audit and automated standing derivation without becoming a second operational database?

### 9.3 OCEL 2.0 replay plane

Marketplace and deployment events can be represented as object-centric event logs. Packs, commits, workflows, qualification shards, artifacts, and releases are natural objects connected by events.

Research question: can the process history itself become the state carrier, allowing release standing and WIP to be reconstructed from event/object relations without a separate workflow-state database?

### 9.4 Formal admission with Lean/mfact

Structural invariants such as acyclic dependency graphs, total navigation ordering, or receipt closure can be promoted from procedural tests into formally admitted propositions where the cost is justified.

Research question: which invariants benefit materially from proof, and how can proof objects remain bound to the same graph/toolchain identities exercised by runtime qualification?

### 9.5 Pack algebra

Composition currently behaves operationally as path-based pack inclusion and semantic graph union. A formal pack algebra could define identity, composition, conflicts, supersession, and closure.

Research question: under what conditions is pack composition associative, and which conflicts require explicit admission rather than implicit merge semantics?

### 9.6 Incremental qualification

A large corpus does not always require requalifying every pack after every change. An impact graph can identify the dependency closure affected by a changed subject.

Research question: how can the marketplace safely reuse prior receipts while proving validator, toolchain, configuration, and dependency identities are equivalent?

### 9.7 Deterministic release capsules

A release could publish a capsule containing source fingerprint, admitted config, ggen identity, qualification receipt DAG, and reproducible catalog/archive artifacts.

Research question: what is the minimal capsule that allows an independent verifier to reconstruct marketplace standing offline?

### 9.8 Multi-target semantic projections

The long-term value of the marketplace lies in one ontology manufacturing many targets: CLI, API, MCP, documentation, tests, policy, telemetry, process models, and formal specifications.

Research question: where does a shared ontology stop being a simplification and become an over-coupled universal schema? The answer should be empirical and domain-specific.

## 10. Metrics for the research program

Future work should track metrics that correspond to architectural claims rather than vanity activity.

### Semantic leverage

`generated consequence types / independently maintained semantic facts`

Higher leverage is valuable only while projection fidelity remains high.

### Replay rate

Fraction of qualified subjects whose second manufacture matches the first consequence digest.

### Evidence lead time

Time from source admission to full required standing.

### Refusal precision

Fraction of failed subjects receiving a typed, localizable refusal instead of generic failure.

### Receipt reuse rate

Fraction of validation work safely reused through proven identity equivalence.

### Drift incidents

Number of cases where generated consequence and canonical semantic source diverge unexpectedly.

### Boundary escape incidents

Number of observed attempts or defects that cross filesystem, dependency, network, or authority bounds.

### Self-hosting coverage

Fraction of marketplace infrastructure manufactured by marketplace packs and exercised through real consumer boundaries.

## 11. What would refute the broader thesis?

The broader research program should be abandoned or substantially revised if repeated evidence shows that:

1. ontology-first models cost more to maintain than the duplicated representations they replace without yielding measurable consistency or reuse benefits;
2. deterministic projection does not materially reduce drift because most relevant behavior remains outside the modeled graph;
3. real consumers require so many pack-specific exceptions that a generic marketplace abstraction collapses;
4. receipt production is too expensive or incomplete to improve auditability over conventional CI logs;
5. strict authority separation imposes enough latency that operators routinely bypass it;
6. replay equivalence is impossible to define for the dominant target domains without effectively snapshotting entire environments;
7. graph composition creates semantic conflicts more complex than the generated reuse it enables;
8. self-hosted pack infrastructure proves less reliable than conventional hand-maintained equivalents over sustained operation.

A research architecture that cannot name its own disconfirming evidence is an ideology, not an engineering theory.

## 12. What would strengthen the thesis?

Conversely, the thesis gains support if the marketplace demonstrates over time that:

- one semantic change safely fans out to many target artifacts;
- replay receipts catch nondeterminism before consumers do;
- exact-subject CI prevents false standing during concurrent repository activity;
- typed refusals reduce repair time;
- self-hosting exposes integration defects earlier than synthetic fixtures;
- public ontology reuse lowers translation cost across packs;
- incremental receipt reuse reduces CI cost without increasing false positives;
- the process/event graph is sufficient to reconstruct operational state and standing;
- independently implemented validators agree on admitted consequences.

## 13. Research ethics and epistemic discipline

The most important governance property is epistemic restraint. High-throughput generation makes overclaiming easier because artifacts appear faster than humans can inspect them. The response cannot be to pretend that every generated artifact has been reviewed. The system must instead make evidence machine-readable enough that standing can scale with manufacture.

Three rules follow.

First, **generated volume is not evidence of correctness**. Throughput matters only when bounded by admission and verification.

Second, **UNKNOWN is a valid state**. The system should prefer a precise unknown over an invented crown.

Third, **failure is topology**. A failed edge reveals where the current system stops. Repair should preserve all other lawful edges and make the new boundary explicit.

These rules are what allow aggressive automation without sacrificing falsifiability.

## 14. Conclusion

The ggen Marketplace can be understood as a semantic software-manufacturing institution whose primary problem is not template distribution but preservation of meaning and evidence across transformations.

Its central pipeline is:

`observation → admission → semantic graph → selection → construction → verification → authorized actuation → receipt → replay → standing`

The mdBook self-hosting experiment makes that pipeline visible in a small but complete domain. The book graph selects navigation. ggen constructs control files. mdBook compiles the static artifact. GitHub Pages performs publication under separate authority. CI receipts bind these transitions to exact source identities.

The architecture succeeds only when these distinctions remain operational, not merely rhetorical. Its strongest claim is therefore also its simplest:

> Software manufacture should be as aggressive as lawful construction permits and as conservative as consequential authority requires, with every crown earned by observed execution against the exact admitted subject.

That principle is the bridge between ontology-first generation, deterministic replay, marketplace governance, and post-agentic software operations.