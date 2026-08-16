# Bibliography and primary sources

## 1. Citation policy

This bibliography prioritizes **primary specifications, project documentation, and foundational research** over secondary summaries. The monograph's architecture deliberately reuses established standards; these references define the semantics that local prose should not reinvent.

The bibliography is not a claim that every cited system endorses ggen Marketplace or that the marketplace fully conforms to every referenced standard. Each citation documents intellectual lineage or a candidate interoperability boundary.

For web specifications, the stable specification URL is preferred when available. Version-sensitive execution evidence remains bound separately through repository receipts and toolchain identities.

## 2. Semantic Web foundations

### [RDF11] RDF 1.1 Concepts and Abstract Syntax

Richard Cyganiak, David Wood, Markus Lanthaler (eds.). **RDF 1.1 Concepts and Abstract Syntax.** W3C Recommendation, 25 February 2014.

<https://www.w3.org/TR/rdf11-concepts/>

Relevance: defines the RDF graph/data model used as the semantic source substrate for marketplace ontology and consumer graphs.

### [SPARQL11] SPARQL 1.1 Query Language

Steve Harris, Andy Seaborne (eds.). **SPARQL 1.1 Query Language.** W3C Recommendation, 21 March 2013.

<https://www.w3.org/TR/sparql11-query/>

Relevance: defines the query language used by ggen templates to select bindings from RDF source. The monograph's ordered-projection claims depend on making order explicit when artifact semantics depend on row order.

### [SHACL] Shapes Constraint Language

Holger Knublauch, Dimitris Kontokostas (eds.). **Shapes Constraint Language (SHACL).** W3C Recommendation, 20 July 2017.

<https://www.w3.org/TR/shacl/>

Relevance: candidate declarative admission layer for graph-local manufacturing constraints such as cardinality, datatype, required properties, and closed local shapes.

### [SKOS] SKOS Simple Knowledge Organization System Reference

Alistair Miles, Sean Bechhofer (eds.). **SKOS Simple Knowledge Organization System Reference.** W3C Recommendation, 18 August 2009.

<https://www.w3.org/TR/skos-reference/>

Relevance: the mdBook pack's pattern language is modeled as a SKOS concept scheme rather than inventing a bespoke taxonomy representation.

### [PROV-O] PROV-O: The PROV Ontology

Timothy Lebo, Satya Sahoo, Deborah McGuinness (eds.). **PROV-O: The PROV Ontology.** W3C Recommendation, 30 April 2013.

<https://www.w3.org/TR/prov-o/>

Relevance: primary provenance vocabulary for representing entities, activities, agents, derivation, and use. The proposed marketplace receipt ontology should reuse PROV-O for generic lineage.

## 3. Requirements language

### [RFC2119] Key words for use in RFCs to Indicate Requirement Levels

Scott Bradner. **RFC 2119 / BCP 14.** Internet Engineering Task Force, March 1997.

<https://www.rfc-editor.org/info/rfc2119>

### [RFC8174] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words

Barry Leiba. **RFC 8174 / BCP 14.** Internet Engineering Task Force, May 2017.

<https://www.rfc-editor.org/info/rfc8174>

Relevance: the normative constitution uses BCP 14 uppercase requirement terms so MUST/SHOULD/MAY have stable interpretation.

## 4. Reproducibility and functional deployment

### [REPRO] Reproducible Builds — Definition

**When is a build reproducible?** Reproducible Builds project.

<https://reproducible-builds.org/docs/definition/>

Relevance: provides the stronger independent-reconstruction notion against which the monograph distinguishes same-runner replay from reproducibility. The experimental chapter's R0–R5 ladder makes that distinction operational.

### [REPRO-DOCS] Reproducible Builds — Documentation

Reproducible Builds project.

<https://reproducible-builds.org/docs/>

Relevance: catalogs environmental variance sources, deterministic-build practices, environment definition, checksums, and verification concerns relevant to semantic projection as well as binary compilation.

### [DOLSTRA] The Purely Functional Software Deployment Model

Eelco Dolstra. **The Purely Functional Software Deployment Model.** PhD thesis, Utrecht University.

Primary research index:

<https://nixos.org/research/>

Relevance: foundational functional-deployment work on explicit dependencies, isolation, and correctness of software deployment. The marketplace treats this as adjacent rather than competing work: Nix governs build/deployment closure, while ggen Marketplace governs semantic source-to-artifact manufacture.

## 5. Source identity and content-addressed history

### [GIT-OBJECTS] Git Internals — Git Objects

Scott Chacon, Ben Straub et al. **Pro Git, 2nd ed., Git Internals: Git Objects.**

<https://git-scm.com/book/en/v2/Git-Internals-Git-Objects>

Relevance: Git's blob/tree/commit graph supplies practical immutable source identities used by the exact-head law and receipt subject binding.

## 6. Software supply-chain integrity

### [IN-TOTO] in-toto Specification and Documentation

**in-toto: a framework to secure the integrity of software supply chains.** CNCF project.

Stable specification index:

<https://in-toto.io/docs/specs/>

Getting-started model:

<https://in-toto.io/docs/getting-started/>

Relevance: layouts, authorized functionaries, materials, products, link metadata, and verification strongly overlap with the marketplace's receipt-DAG and authority concerns. Future receipt export should prefer interoperability over incompatible reinvention.

### [SLSA12] SLSA v1.2 Provenance

**Supply-chain Levels for Software Artifacts — Provenance, Version 1.2.**

<https://slsa.dev/spec/v1.2/provenance>

Relevance: defines provenance as verifiable information tracking artifacts through supply-chain production. The marketplace receipt model should map builder/toolchain, subject, dependencies, and outputs to SLSA/in-toto concepts where semantics align.

## 7. Process intelligence

### [OCEL20] Object-Centric Event Log 2.0

**OCEL 2.0 Specification.** Object-Centric Event Log standard.

<https://www.ocel-standard.org/specification/overview/>

Relevance: provides a multi-object event model suitable for executions involving commits, packs, workflows, artifacts, receipts, and releases simultaneously. The monograph proposes, but has not yet proved, that an OCEL/event graph can become sufficient process-state evidence for portions of marketplace operation.

## 8. Documentation architecture and publication

### [DIATAXIS] Diátaxis

Daniele Procida. **Diátaxis: a systematic approach to technical documentation authoring.**

<https://diataxis.fr/>

Primer:

<https://diataxis.fr/start-here/>

Relevance: defines tutorials, how-to guides, reference, and explanation as distinct documentation modes. ggen Marketplace preserves these modes and layers a research monograph over them rather than flattening operational documentation into dissertation prose.

### [MDBOOK] mdBook Documentation

Rust project. **mdBook — create books from Markdown files.**

<https://rust-lang.github.io/mdBook/>

Source repository:

<https://github.com/rust-lang/mdBook>

Relevance: independent target compiler used by the self-hosting documentation experiment. The marketplace workflow intentionally pins a released mdBook version and treats successful `mdbook build` as target-compiler evidence rather than assuming generated metadata is valid.

## 9. Marketplace-local primary sources

The repository itself contains executable and normative sources that should be cited by exact commit when used outside the repository.

### [GGM-AGENTS] Repository operating contract

`AGENTS.md`.

Defines source hierarchy, branching discipline, pack identity, deterministic validation, generated-source rules, and evidence boundaries.

### [GGM-MARKETPLACE] Marketplace operational configuration

`marketplace.toml`.

Defines canonical repository/toolchain/policy inputs admitted by the marketplace configuration court.

### [GGM-VALIDATOR] Marketplace acceptance calculus

`scripts/marketplace.py` and supporting scripts.

Defines pack discovery, structural validation, deterministic catalog/archive behavior, source fingerprints, and related repository courts.

### [GGM-QUAL] Pack qualification court

`scripts/qualify_packs.py` and `scripts/qualify-marketplace.sh` or their current admitted equivalents.

Defines isolated real-ggen qualification, replay, source mutation checks, and qualification evidence.

### [GGM-MDBOOK-PACK] mdBook pattern-language pack

`packs/mdbook-pattern-language-pack/`.

Defines ontology-first book metadata/navigation and deterministic projection to mdBook control files.

### [GGM-BOOK-GRAPH] ggen Marketplace book graph

`docs/book.ttl`.

Defines the self-hosting book identity and ordered navigation. `docs/SUMMARY.md` and root `book.toml` are generated reviewable consequences.

### [GGM-PAGES] GitHub Pages workflow

`.github/workflows/pages.yml`.

Defines exact-subject checkout, admitted ggen installation, semantic manufacture, pinned mdBook compilation, and main-only Pages actuation.

## 10. Citation map by chapter

| Chapter | Primary references |
|---|---|
| Research program | RDF11, PROV-O, REPRO, GGM local sources |
| Formal calculus | RDF11, SPARQL11, BCP14, REPRO |
| Ontology/compiler architecture | RDF11, SPARQL11, SHACL, SKOS |
| Authority/receipts/standing | PROV-O, IN-TOTO, SLSA12, GIT-OBJECTS |
| Verification/security/evaluation | REPRO, IN-TOTO, SLSA12 |
| Self-hosting case study | MDBOOK, DIATAXIS, GGM-MDBOOK-PACK, GGM-PAGES |
| Theorem catalogue | all above as semantic/implementation premises |
| Related work | all external references |
| Experimental methods | REPRO, OCEL20, GGM qualification sources |
| Pack algebra | RDF11, SHACL, PROV-O |
| Evidence economics | repository event/receipt datasets + queueing theory to be added in future scholarly bibliography |
| Normative constitution | RFC2119, RFC8174 + executable repository law |
| Receipt schema | PROV-O, IN-TOTO, SLSA12, GIT-OBJECTS |

## 11. Deliberately missing scholarly domains

A serious literature review should expand beyond the current primary-source core before external academic publication. Priority areas include:

- model-driven engineering and model-to-text transformation;
- software product lines and feature models;
- build systems and incremental computation;
- proof-carrying code and proof-carrying data;
- capability security and object-capability models;
- event sourcing and temporal databases;
- process mining and conformance checking;
- software architecture description languages;
- reproducible research and computational notebooks;
- software economics and coordination theory;
- continuous integration empirical research;
- program synthesis and neurosymbolic systems.

These are marked as literature-review work rather than filled with guessed citations. The book prefers an explicit gap over fabricated completeness.

## 12. Source-quality rule

For future additions:

1. prefer standards body specifications for standard semantics;
2. prefer original papers/theses for foundational research claims;
3. prefer official project documentation for tool behavior;
4. distinguish current implementation docs from historically cited versions;
5. bind execution-specific claims to exact repository/toolchain receipts;
6. do not use a marketing page to support a formal systems claim when a specification exists;
7. do not imply that citation establishes conformance.

The bibliography's role is to make the intellectual boundary of the work inspectable. The executable courts remain responsible for proving what this repository actually does.
