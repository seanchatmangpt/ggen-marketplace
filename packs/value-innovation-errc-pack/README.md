# value-innovation-errc-pack

A domain-neutral Eliminate/Reduce/Raise/Create strategy kernel for the ggen ecosystem.

## Why this exists

`gh-actions-errc-pack` proved that ERRC can be represented as evidence-bounded RDF with native SPARQL gates, but its namespace and `Finding` semantics are intentionally bound to GitHub Actions. `domain-capability-pack` then had to reuse that GitHub-specific vocabulary for a non-GitHub domain. That is a reuse smell: the strategy calculus is more general than either consumer.

This pack extracts the reusable invariant while preserving the original pack as historical/proven evidence.

## ERRC protocol

A consumer supplies a `vi:StrategyGrid` and typed `vi:Finding` instances. Every finding names:

- exactly one of Eliminate, Reduce, Raise, Create
- the factor being changed
- baseline and target
- rationale
- bounded owner and intended consumer
- evidence obligation
- falsifier
- explicit `directActuation false`

A grid may claim `vi:complete true` only when all four actions are represented.

## Innovation beyond a four-box workshop

The pack turns ERRC into an executable strategy contract:

`observation → factor → action → target → owner → evidence obligation → falsifier → standing`

The four quadrants are therefore not prose recommendations. They are typed, queryable manufacturing inputs.

### Authority law

ERRC has no ambient DO authority. `Create` is particularly constrained: it can construct a reversible proposal, specification, template, pack, work order, or candidate artifact, but execution still belongs to the consumer's authorized actuation path.

### Evidence law

`ALIVE` is refused unless the subject links verified evidence. A strategy document can establish a proposal; it cannot certify its own business consequence.

### Value-innovation hypothesis

A grid can state the value it expects to raise, the waste/friction it expects to reduce, and a falsifiable test. This makes Blue Ocean-style value innovation compatible with PDCA, DfCM, platform reuse, and process evidence rather than treating innovation as an unmeasured brainstorming exercise.

## Public semantics

The vocabulary uses PROV-O for provenance-compatible entities, DCTERMS for identity/description, and SKOS for controlled ERRC/standing concepts. Consumer ontologies can connect additional public vocabularies without changing the kernel.

## Migration strategy

Do not rewrite `gh-actions-errc-pack` historical evidence merely to use this namespace. New cross-domain work should use `value-innovation-errc-pack`; existing specialized packs can progressively map their local vocabulary to this kernel while preserving replayability and historical identity.
