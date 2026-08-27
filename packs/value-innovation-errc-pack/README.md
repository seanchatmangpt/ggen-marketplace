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

`observation → factor → option topology → action → target → owner → evidence obligation → falsifier → standing`

The four quadrants are therefore not prose recommendations. They are typed, queryable manufacturing inputs.

### Strategy canvas / value curve

`vi:StrategyCanvas` is a W3C RDF Data Cube dataset. A complete canvas contains a baseline and target `vi:ValueCurve`; each `vi:CurvePoint` is a factor observation with a numeric `vi:offeringLevel` from 0 through 10. This makes the before/after value curve queryable and deterministic rather than a hand-drawn chart.

### Pareto evidence

`vi:ParetoClaim` imports the reusable part of the specialized GitHub-Actions precedent: a claim must bind the finding, an evidence witness, a protected invariant, and dimension deltas. A protected dimension may not be `vi:Worse`, and at least one dimension must be `vi:Better`.

### DfCM composition

The pack does not clone Design for Combinatorial Maximalism. A grid may link the existing `cmd:DesignSpace`, and a finding may select an existing `cmd:Candidate`. If linked, the candidate must already have `cmd:standing "VERIFIED"`. CMD remains authoritative for option-space construction and actuation law.

### Authority law

ERRC has no ambient DO authority. `Create` is particularly constrained: it can construct a reversible proposal, specification, template, pack, work order, or candidate artifact, but execution still belongs to the consumer's authorized actuation path. The v0.2 gate requires `vi:reversibleProposal true` on every Create finding.

### Evidence law

`ALIVE` is refused unless the subject links verified evidence. A strategy document can establish a proposal; it cannot certify its own business consequence.

### Value-innovation hypothesis

A grid can state the value it expects to raise, the waste/friction it expects to reduce, and a falsifiable test. This makes value innovation compatible with PDCA, DfCM, platform reuse, and process evidence rather than treating innovation as an unmeasured brainstorming exercise.

## Public semantics

The vocabulary uses PROV-O for provenance-compatible entities, DCTERMS for identity/description, SKOS for controlled concepts, and W3C RDF Data Cube for strategy-canvas observations. Optional CMD links reuse the existing `ggen-combinatorial-maximalism-pack` vocabulary.

## Migration strategy

Do not rewrite `gh-actions-errc-pack` historical evidence merely to use this namespace. New cross-domain work should use `value-innovation-errc-pack`; existing specialized packs can progressively map their local vocabulary to this kernel while preserving replayability and historical identity.
