# Ontology and compiler architecture

## 1. The marketplace as a compiler system

A template marketplace is usually described as content distribution: locate a template, copy it, substitute variables, and own the resulting files. ggen Marketplace is better modeled as a **semantic compiler system**. Its canonical inputs are not just text fragments but typed graph facts and bounded generation contracts. The generated file tree is a projection of that source model.

The compiler analogy is exact only when its correspondences are stated carefully:

| Compiler concept | Marketplace realization |
|---|---|
| source language | RDF facts plus pack identity/configuration |
| intermediate representation | admitted graph selected by SPARQL |
| optimization/selection | query-level filtering and ordering |
| code generation | bounded templates |
| target language | Markdown, Rust, TOML, YAML, source trees, or other files |
| static checks | schema, RDF parse, gates, marketplace validation |
| execution test | real ggen sync against a consumer capsule |
| reproducibility check | second sync and consequence comparison |
| package/distribution unit | marketplace pack |

This framing matters because compiler architecture imposes stronger obligations than “file templating.” A compiler needs an input model, a transformation law, target identity, deterministic ordering where order is semantic, failure modes, and a way to reason about versioned source.

## 2. Why RDF is the intermediate representation

The marketplace uses RDF because reusable software models are fundamentally relational. A command belongs to a noun; a generated module implements a capability; a documentation chapter occupies a position; a policy applies to a resource; an artifact derives from a source; a pack supersedes another pack. Representing those facts as a graph preserves relations that a flat variable map tends to erase.

Three properties are especially important.

### 2.1 Open composition

A graph can combine facts from multiple ontologies without requiring a single giant schema. A pack can reuse public vocabulary for provenance, labeling, concepts, datasets, units, observations, or policy while defining local terms only where needed.

The architectural preference is:

`public ontology → reused IRI → local extension only for irreducible semantics`

This reduces semantic duplication. Re-minting a local concept that is already represented by a stable public ontology increases translation cost and makes cross-pack composition harder.

### 2.2 Queryable projection

SPARQL makes the selection edge explicit. A template need not navigate an arbitrary in-memory object tree or rely on hidden application code. It can declare the graph pattern that admits rows to the projection. The query therefore becomes part of the manufacturing contract.

For the mdBook pack, the essential query is conceptually:

```sparql
SELECT ?position ?kind ?title ?path
WHERE {
  ?entry a mdp:NavigationEntry ;
         mdp:position ?position ;
         mdp:kind ?kind ;
         dcterms:title ?title .
  OPTIONAL { ?entry mdp:path ?path }
}
ORDER BY ?position
```

The template's behavior is then bounded by a visible relation: ordered navigation entries become `SUMMARY.md` rows.

### 2.3 Projection multiplicity

One graph can support multiple projections. A command graph may generate a CLI dispatch table, reference documentation, tests, JSON schema, or MCP surface without duplicating the command inventory in each target format. This is the primary economic advantage of an ontology-first source model: one semantic change can lawfully fan out into many mechanically related artifacts.

The constraint is that each projection must remain reviewable. Multiplicity is useful only when generated consequences can be traced back to the graph facts and template that produced them.

## 3. Public ontologies as semantic infrastructure

The marketplace's ontology-first stance is strongest when it avoids unnecessary private vocabularies. Several public standards are natural building blocks:

- **RDF/RDFS** for graph structure and basic classes/properties.
- **SKOS** for controlled concept schemes and pattern languages.
- **PROV-O** for derivation, entities, activities, and agents.
- **Dublin Core Terms** for titles, creators, identifiers, language, and generic metadata.
- **DCAT** where packs or generated outputs are modeled as distributable data assets.
- **ODRL** where policy and permission need semantic representation.
- **SHACL** where graph-shape validation is the appropriate admission mechanism.
- **QUDT** where quantities and units are part of the domain.
- **SOSA/SSN** where observation and sensing semantics are relevant.
- **OCEL 2.0 concepts** where event/object execution history is part of state or replay evidence.

Public ontology reuse is not a purity rule. A concept should be reused only when its semantics actually match. A false equivalence is worse than a local term. The rule is equivalence before analogy: prove that the public concept inhabits the same system boundary before substituting it.

## 4. Pack anatomy as a language module

A marketplace pack has a deliberately small source hierarchy.

### `pack.toml`

Declares pack identity and pack-level metadata. Directory name and declared name must agree. Identity is separate from the ontology because consumers and marketplace tooling need a stable administrative handle even when domain facts evolve.

### `ontology.ttl`

Carries semantic source facts. In projection-oriented packs, this is the highest-information artifact because it expresses objects and relations from which several targets may be generated.

### `templates/`

Contains bounded projection logic. Templates should not become hidden databases. If a domain fact changes the generated result, the fact belongs in the graph or another admitted source rather than being silently encoded in prose inside the template.

### `gates/`

Optional validation surfaces that may refuse a graph before generation. A gate is not a general execution hook. Its purpose is admission/refusal, not ambient actuation.

### `qualification/`

Contains consumer-side fixtures used to exercise the pack at the real ggen boundary. Qualification data should demonstrate the pack, not smuggle target outputs into the source.

### `ggen.toml`

For project-profile packs or consumers, describes the generation contract. It belongs to the ggen execution model, not the marketplace's global catalog law.

## 5. Source, IR, projection, consequence

The architecture can be written as a four-stage compiler relation:

`S → G → P → A`

where:

- `S` is admitted semantic source;
- `G` is the graph available to the compiler;
- `P` is a selected/query result relation;
- `A` is the generated artifact set.

For a fixed toolchain `T`, the manufacturing relation is:

`A = render_T(query(G), templates)`

The key discipline is that `A` does not automatically become a new canonical source. If `A` is committed for reviewability, it is a checked-in consequence. The graph/template pair remains the source from which drift can be detected.

This is the conceptual reason the marketplace refuses a hand-maintained second catalog. If catalog rows can be derived from pack source, independently editing a catalog creates two competing authorities.

## 6. Generated projections and freeze policy

Generated files create a subtle source-control problem. There are two legitimate goals:

1. allow deterministic regeneration;
2. preserve human edits when generated consequences are intentionally reviewable.

A freeze/checksum policy can make manual drift visible rather than silently overwriting it. This is a fail-closed choice: if the source graph changes and a generated file no longer matches its stored consequence, the system may require an explicit regeneration step rather than replacing bytes implicitly.

The broader principle is that generated artifacts need a **mutation policy**. “Generated” is not a sufficient policy by itself. The system must specify whether outputs are disposable, reviewable, frozen, overwritten, or refused when drift is detected.

## 7. Graph composition and dependency closure

A pack may reference another pack's ontology or generation behavior. The resulting dependency graph has two distinct edge types that should not be confused.

### Semantic dependency

Pack `A` uses terms or facts defined by pack `B`. This may be represented by reused IRIs or explicit extra ontologies.

### Operational dependency

Pack `A` requires pack `B` to be present as a generation dependency in a consumer project.

Semantic reuse does not necessarily imply operational composition. Conversely, a project can operationally compose two packs that share no ontology namespace.

Qualification must therefore reconstruct the dependency shape needed by the actual ggen boundary. The marketplace's qualification capsule copies composed sibling packs only when the consumer contract requires them, preserving relative path semantics while refusing paths that escape the bounded packs root.

This is a concrete example of a general law:

> Materialize the dependency-closed subtree required by the selected execution path; do not confuse a connector-visible object graph with an executable local tree.

## 8. The mdBook pattern language as a minimal example

The mdBook pack illustrates the architecture in a domain small enough to inspect completely.

The graph defines a `Book` and ordered `NavigationEntry` objects. Each entry has a position, kind, title, and optionally a path. The templates project two control surfaces:

- `book.toml`, containing compiler configuration;
- `docs/SUMMARY.md`, containing ordered navigation.

Existing Markdown chapters remain outside the pack because the pack is a **pattern language for book structure**, not the owner of every consumer's prose. This separation allows the same pack to organize a different repository without importing marketplace-specific text.

Self-hosting then adds a consumer ontology, `docs/book.ttl`, whose entries describe the marketplace book. The same pack that can be distributed to other consumers therefore manufactures its own marketplace documentation control surfaces.

## 9. Category-theoretic reading

The architecture admits a useful categorical interpretation without requiring category theory for implementation.

Consider admitted domain graphs as objects in a category `G`, and deterministic semantics-preserving graph transformations as morphisms. Consider artifact trees as objects in a category `F`, with bounded filesystem transformations as morphisms. A pack behaves like a partial functor-like mapping from a subcategory of `G` into `F`:

`M : G_admitted ⇀ F`

The mapping is partial because some graphs are refused. Composition is meaningful when the codomain of one stage is lawfully admitted as the domain of the next.

The practical value of this viewpoint is the composition law. If `f` and `g` are separately lawful but `g ∘ f` crosses an undeclared authority boundary or loses identity, then the composed system is not lawful merely because each local function exists. Composition itself needs admission.

## 10. Compiler correctness claims

A marketplace pack may make several increasingly strong claims.

### Level 0 — Parseable

Pack metadata, RDF, and templates are structurally readable.

### Level 1 — Selectable

Queries execute and return the intended domain relation.

### Level 2 — Generative

A real ggen runtime manufactures non-empty bounded consequences.

### Level 3 — Replay-convergent

Repeated generation over equivalent admitted input produces the same consequence digest.

### Level 4 — Behaviorally verified

A target-specific validator executes generated behavior and observes the claimed semantics.

### Level 5 — Operationally receipted

Consequential deployment or actuation is performed with explicit authority and a replayable receipt.

These levels are intentionally not collapsed. Marketplace qualification generally proves Levels 1–3 for its filesystem generation boundary. A generated cloud service, CLI, or runtime may need separate Level 4–5 evidence.

## 11. Falsifiers for ontology-first manufacture

The ontology/compiler model would be weakened or refuted by any of the following observations:

- a semantically important output change that cannot be traced to source graph, template, toolchain, or explicit configuration;
- a required second catalog that must be manually synchronized with pack source;
- query results whose ordering affects output but is left unspecified;
- dependency composition that silently escapes the admitted pack root;
- template logic that embeds authoritative domain facts unavailable in the graph;
- generated output that is treated as canonical while the graph is allowed to drift independently;
- self-hosting that requires marketplace-specific exceptions inside the generic mdBook pack.

The goal is not to ban every exception. It is to make exceptions visible as changes to the architectural claim.

## 12. Consequence

Once the marketplace is treated as a compiler system, documentation, CI, packaging, and security become aspects of the same problem: preserve identity and semantics while moving from graph facts to executable or publishable consequences. The next chapter examines the authority boundary that prevents this compiler power from becoming ambient execution authority.