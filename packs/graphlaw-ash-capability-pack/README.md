# graphlaw-ash-capability-pack

Projects a typed Elixir capability surface for `AshGraphLaw` from the GraphLaw capability
registry. The pack exposes what GraphLaw already supports; it never reimplements RDF, SPARQL,
SHACL, ShEx, N3, Datalog, entailment or planning semantics.

## Identity

- Semantic source: `ontology.ttl` (namespace `http://seanchatmangpt.github.io/packs/graphlaw-ash-capability#`, prefix `gac:`).
- Registry schema consumed: `graphlaw.capability-registry/1` (GraphLaw 26.9.29, ABI version 1).
- Target language: `ex` (`targets.toml`).

## Inputs

The consumer's `ontology.ttl` supplies, as RDF individuals under `https://graphlaw.dev/registry#`:

1. The registry statements emitted by `graphlaw-registry --print-ttl` (classes `gac:Registry`,
   `gac:Capability`, `gac:ResponseVariant`, `gac:CapabilityField`, `gac:EnumValue`,
   `gac:Dialect`, `gac:RefusalCode`, `gac:LawStep`, `gac:VocabularyEntry`, `gac:Limit`).
2. Consumer-supplied `gac:OpBinding` individuals (`gac:bindingOp`, optional
   `gac:bindingResultModule`, `gac:bindingLegacy`).

The vocabulary in this pack's `ontology.ttl` carries no sample individuals. A reduced
three-operation positive consumer lives in `qualification/consumer.ttl`; its digests are
fixture strings, not real registry digests.

## Outputs

Generated Elixir (never hand-edited by the consumer):

- `AshGraphLaw.Capability` behaviour and `AshGraphLaw.Capability.Registry`
- `AshGraphLaw.Capability.<Op>` per registry operation and `AshGraphLaw.Capability.API`
- `AshGraphLaw.Result.Term` and `AshGraphLaw.Result.<Op>` (operations without a
  `gac:bindingResultModule` override)
- `documentation/reference/capabilities.md` and one reference page per operation
- `test/generated/capability_surface_test.exs` (pure, no wasm)

Gates compare against `gac:opCount`; no gate hardcodes the operation count.

## Wiring

1. Vendor the pack into the consumer (`scripts/vendor_marketplace.sh`).
2. Import the registry RDF into the consumer `ontology.ttl` between the
   `BEGIN GENERATED-REGISTRY` and `END GENERATED-REGISTRY` markers, and add `gac:OpBinding`
   individuals.
3. List the pack under `[packs]` in the consumer `ggen.toml` and run `ggen sync`.

## Evidence boundary

Marketplace admission and ggen qualification (render plus gates) only. Semantic success is
PARTIAL_ALIVE at most; no execution authority is granted.
