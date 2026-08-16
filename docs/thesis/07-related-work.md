# Related work, intellectual lineage, and distinguishing claims

## 1. Research positioning

The ggen Marketplace does not claim to invent graphs, templates, reproducible builds, provenance, software supply-chain attestations, formal constraints, process mining, or technical documentation architecture. Its research contribution is the **composition of these ideas into a deterministic semantic manufacturing institution** with an explicit separation between observation, admission, construction, actuation, receipts, replay, and standing.

That distinction matters. Novelty claims become fragile when a project presents a known primitive as though it were unprecedented. A stronger position is to identify which concepts are inherited, which are recombined, and which system-level consequences are specific to the marketplace architecture.

This chapter therefore separates:

- **borrowed foundations** — established standards and prior systems;
- **architectural synthesis** — how those foundations are connected here;
- **distinguishing claims** — propositions the marketplace must support empirically or formally;
- **non-claims** — boundaries where the project should not imply superiority or priority.

Primary references are collected in the bibliography appendix.

## 2. RDF as semantic intermediate representation

RDF defines a graph-based abstract data model in which information is expressed as triples. The marketplace uses that model as a semantic intermediate representation for manufacturing inputs. This is inherited technology, not a new data model.

### What RDF contributes

- globally identifiable terms through IRIs;
- graph union as a simple composition primitive;
- a mature ecosystem of serializations and query tools;
- separation between abstract graph semantics and concrete syntax;
- interoperability with vocabularies such as PROV-O and SKOS.

### What the marketplace adds

The marketplace treats an admitted RDF graph as **compiler input**. The important transition is not RDF storage but:

`admitted graph → explicit selection → bounded projection → executable evidence`.

The distinguishing claim is therefore not “graphs are useful.” It is:

> A reusable software generator can gain source singularity and compositional leverage when semantic facts are represented in a graph and target artifacts are treated as deterministic projections rather than independent authorities.

That claim requires evidence about maintenance cost, drift, reuse, and replay; RDF alone does not prove it.

## 3. SPARQL as selection language

SPARQL 1.1 provides a standardized query language for RDF graphs. ggen templates use queries to select bindings from semantic source.

This supplies a clean separation:

`G --Q--> bindings --T--> artifact`.

The architecture benefits because query behavior is inspectable and because ordering, optionality, aggregation, and filtering can be made explicit before template rendering.

The marketplace's additional discipline is that **selection is not actuation**. A query may enumerate many possible consequences without granting them permission to execute.

## 4. SHACL and admission constraints

SHACL defines a language for describing and validating constraints over RDF graphs. It is directly relevant to the marketplace's admission layer.

The marketplace currently has a mixed constraint stack: repository validators, native gates, target compilers, and graph conventions. SHACL offers a path for moving graph-local invariants into a declarative, interoperable layer.

Examples include:

- exactly one path for a chapter entry;
- allowed navigation kinds;
- required pack identity fields;
- datatype constraints for positions;
- closed local shapes around manufacturing contracts.

SHACL does **not** replace runtime qualification. A shape can prove that an RDF graph satisfies declared constraints; it cannot prove that ggen, a target compiler, a filesystem, or a deployment platform will execute successfully.

This reinforces the book's evidence ladder rather than collapsing it.

## 5. SKOS and pattern-language vocabulary

SKOS provides a lightweight model for knowledge organization systems. The mdBook pack uses a SKOS concept scheme to describe documentation/manufacturing patterns such as ontology-first navigation, generated summary projection, and exact ordering.

This is an appropriate use because the pattern language is a controlled conceptual organization, not a set of executable class constraints.

The distinction between SKOS concepts and executable admission rules is important: a concept can document a design principle while SHACL or code enforces a constraint. Treating prose taxonomy as validation would be a category error.

## 6. PROV-O and receipt lineage

PROV-O defines a vocabulary for provenance over entities, activities, and agents. The marketplace's receipt model is closely aligned with provenance questions:

- which subject was used;
- which activity executed;
- which agent or authority performed it;
- which artifact resulted;
- which earlier evidence it derived from.

The marketplace should reuse PROV-O for general provenance relations rather than create a parallel vocabulary for concepts that already exist.

The marketplace-specific extension is **standing derivation**. Provenance tells us what happened and how objects relate. Standing asks whether a particular current claim has sufficient, exact, non-stale evidence. A receipt ontology can therefore be PROV-O-compatible without pretending that PROV-O itself defines `ALIVE`, `BLOCKED`, or typed refusal semantics.

## 7. Reproducible Builds

The Reproducible Builds project defines reproducibility in terms of independently recreating bit-for-bit identical specified artifacts from the same declared source, environment, and build instructions.

This is a stronger standard than merely running a generator twice in one CI environment.

The marketplace currently distinguishes several levels:

- deterministic intent;
- same-subject replay convergence;
- isolated qualification replay;
- cross-runner reproducibility;
- independent reconstruction from a release capsule.

The important intellectual debt is that **environment belongs to the build subject**. If a timestamp, locale, dependency version, filesystem order, or toolchain changes output, then it was never irrelevant merely because the configuration omitted it.

The marketplace extends this insight from binary builds to semantic projections and qualification receipts.

## 8. Nix and purely functional deployment

Nix's research lineage demonstrates the power of treating software deployment components as function-like values with explicit dependencies and isolation. The overlap with ggen Marketplace is substantial at the level of philosophy:

- explicit inputs;
- content-addressed or identity-bound artifacts;
- minimized ambient state;
- reproducibility as an architectural property;
- dependency structure as part of correctness.

The systems operate at different layers.

Nix is primarily a deployment/build model for software components and environments. ggen Marketplace is primarily a semantic manufacturing/distribution model for **source-level artifact families** generated from ontology/query/template contracts.

They should therefore be understood as complementary. A ggen-manufactured project may itself be built in Nix; a Nix expression could be generated from semantic source. Neither subsumes the other.

## 9. Git content-addressed object graphs

Git's internal model uses content-addressed blobs, trees, and commits connected into an object graph. This provides the marketplace with a practical immutable subject identity at repository scale.

The exact-head law depends on this distinction:

- branch names are mutable routing references;
- commits identify specific history objects;
- trees identify specific filesystem snapshots;
- blobs identify file content.

The marketplace does not need to invent a new repository identity system. It needs to make receipts consistently bind to the immutable identities Git already exposes.

A future receipt system may include both commit and tree identity because the commit proves historical lineage while the tree directly identifies the executed repository snapshot.

## 10. in-toto

in-toto protects software supply-chain integrity by defining authorized steps and recording link metadata about materials, products, commands, and actors. Its structure is strongly relevant to `SELECT/CONSTRUCT/DO` and receipt DAGs.

Shared concerns include:

- authorized functionaries;
- expected step sequence;
- artifact materials and products;
- cryptographically verifiable evidence;
- verification that the intended chain actually occurred.

The marketplace should not duplicate mature supply-chain attestation formats without reason. A future release capsule could export or map receipts into in-toto attestations.

The distinguishing marketplace concern is that a pack's **semantic manufacture** itself is a first-class subject. The system wants evidence not only that “a build step ran,” but that admitted graph/query/template identities manufactured a bounded consequence, replayed, preserved source, and did not silently acquire actuation authority.

## 11. SLSA provenance

SLSA provenance records verifiable information about how software artifacts were produced, including the build definition, builder identity, external parameters, dependencies, and outputs.

This aligns closely with the marketplace's insistence that receipts name:

- exact subject;
- toolchain/builder;
- relevant inputs;
- consequence identity;
- execution boundary.

SLSA is especially useful as a guard against inventing a bespoke provenance format that omits standard supply-chain concepts.

The marketplace's broader standing model remains distinct. SLSA provenance answers a supply-chain integrity question. Marketplace standing additionally models:

- partial execution;
- blocked boundaries;
- unsupported capabilities;
- typed refusals;
- evidence expiry/equivalence;
- composition of semantic qualification receipts.

A mature implementation should seek interoperability, not replacement.

## 12. OCEL 2.0 and object-centric process evidence

OCEL 2.0 represents events connected to multiple objects and supports object-to-object relationships. This is a natural fit for marketplace execution history because one event may simultaneously concern:

- a commit;
- a pack;
- a qualification fixture;
- a workflow run;
- a generated artifact;
- a release;
- a deployment environment.

A conventional case-centric log forces one primary case identifier. Marketplace operations are inherently multi-object.

The research opportunity is to treat OCEL not merely as analytics telemetry but as a **replayable evidence plane**. If receipts and process events share identities, standing can potentially be reconstructed from event/object relations rather than maintained in a separate mutable workflow database.

That is an open hypothesis, not yet an established result.

## 13. Diátaxis

Diátaxis separates documentation into tutorials, how-to guides, reference, and explanation according to reader need. The marketplace keeps these modes intact and adds a research-monograph mode above them.

This avoids a common documentation failure in which a long research narrative replaces operational usability.

The book therefore has two orthogonal axes:

- **task axis** — Diátaxis documentation for users/operators;
- **theory axis** — monograph chapters for architecture, formalization, evaluation, and research.

The mdBook navigation graph connects both without requiring one genre to impersonate the other.

## 14. mdBook

mdBook is a Markdown book compiler whose structure is controlled by `book.toml` and `SUMMARY.md`. The marketplace uses mdBook as an independent target compiler.

The contribution is not a new book renderer. The experiment asks whether the **control surface for an existing book can itself be manufactured semantically**:

`docs/book.ttl → ggen → book.toml + SUMMARY.md → mdBook → static site`.

This makes mdBook valuable precisely because it is independent. If the generated control files are malformed, the target compiler rejects them. That rejection is stronger evidence than a template unit test claiming the files “look right.”

## 15. Conventional template engines and code generators

Template engines already support deterministic text rendering when given deterministic inputs. Model-driven engineering and code-generation systems have likewise treated higher-level models as source for decades.

The marketplace does not distinguish itself by the mere existence of templates or generation.

Its stronger claim is the integration of:

1. semantic graph source;
2. explicit query selection;
3. reusable distributable packs;
4. deterministic replay qualification;
5. source non-mutation;
6. exact-subject CI;
7. authority separation;
8. typed standing;
9. self-hosting consumer evidence.

This is a **system architecture claim**, not a primitive novelty claim.

## 16. Probabilistic AI systems

Probabilistic language models and agents are capable of planning, interpretation, synthesis, exception handling, and search. The marketplace architecture does not require rejecting them.

Instead, it draws a boundary around where probabilistic reasoning is trusted.

A useful division is:

`probabilistic explore / interpret / propose`

→ `deterministic admit / manufacture / qualify / actuate under policy`.

This architecture can exploit high-capacity reasoning without making a fluent model response itself the authority for irreversible action.

The empirical question is whether this split preserves enough flexibility while materially improving reproducibility and auditability. It should be benchmarked against both manual and agentic alternatives rather than assumed superior.

## 17. Distinguishing-claim matrix

| Concern | Prior art contributes | Marketplace-specific synthesis |
|---|---|---|
| semantic representation | RDF | admitted graph as manufacturing IR |
| selection | SPARQL | query boundary explicitly separated from construction/DO |
| graph validation | SHACL | admission layer tied to executable qualification |
| conceptual taxonomy | SKOS | reusable manufacturing pattern language |
| provenance | PROV-O | provenance plus claim-scoped standing |
| reproducibility | Reproducible Builds | projection replay + release-capsule ladder |
| functional deployment | Nix | semantic source families rather than package closure |
| source identity | Git | exact-head law for receipts |
| supply-chain integrity | in-toto | semantic manufacture as evidence-bearing step |
| build provenance | SLSA | typed standing/refusal and receipt closure |
| process evidence | OCEL 2.0 | candidate state/evidence carrier for multi-object workflows |
| documentation architecture | Diátaxis | operational docs plus executable research monograph |
| book compilation | mdBook | self-hosted semantic navigation/control projection |

## 18. Novelty must be decomposed

The research program should avoid a binary “novel/not novel” argument. Instead evaluate novelty at four levels.

### N1 — Primitive novelty

Are individual mechanisms new?

Mostly no. RDF, SPARQL, templates, CI, provenance, reproducibility, and process logs have extensive prior art.

### N2 — Composition novelty

Is this particular combination of semantic manufacturing, exact evidence, authority separation, and self-hosting marketplace qualification uncommon or technically distinctive?

This is the strongest current novelty candidate and requires comparative literature review plus implementation evidence.

### N3 — Operational novelty

Does the system make previously manual or ambiguous governance computable at materially higher scale?

This requires longitudinal measurements: repair time, drift incidents, receipt reuse, semantic leverage, and WIP throughput.

### N4 — Theoretical novelty

Do the pack algebra, standing calculus, or bounded-receipt model establish useful formal results not already implied by established build/provenance systems?

This is still OPEN and should be evaluated through mechanization and peer comparison.

## 19. Non-claims

The book intentionally does **not** claim that:

- RDF is universally superior to other intermediate representations;
- deterministic systems are automatically correct or secure;
- ggen replaces general-purpose programming languages;
- marketplace qualification proves all generated runtime behavior;
- receipts eliminate the need for trusted execution environments or human governance;
- self-hosting proves universal pack correctness;
- supply-chain standards such as SLSA or in-toto are made obsolete;
- every profession or workflow should be modeled as a pack;
- probabilistic AI has no legitimate role in software manufacture.

These exclusions strengthen the central thesis by keeping it falsifiable.

## 20. The synthesis claim

The most defensible high-level contribution is:

> ggen Marketplace treats software generation as a governed semantic manufacturing pipeline in which model source, selection, construction, authority, provenance, replay, and standing are separate first-class objects that can be composed and independently falsified.

The research burden is now explicit. The next chapter defines how to test whether that synthesis actually improves outcomes.
