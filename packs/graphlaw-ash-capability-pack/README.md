# graphlaw-ash-capability-pack

Projects a typed Elixir capability surface for `AshGraphLaw` from the GraphLaw capability
registry. The pack exposes what GraphLaw already supports; it never reimplements RDF, SPARQL,
SHACL, ShEx, N3, Datalog, entailment or planning semantics.

## Identity

- Semantic source: `ontology.ttl` (namespace `http://seanchatmangpt.github.io/packs/graphlaw-ash-capability#`, prefix `gac:`).
- Registry schema consumed: `graphlaw.capability-registry/1` (GraphLaw 26.9.29, ABI version 1; pack version 26.9.30).
- Target language: `ex` (`targets.toml`).

## Inputs

The consumer's `ontology.ttl` supplies, as RDF individuals under `https://graphlaw.dev/registry#`:

1. The registry statements emitted by `graphlaw-registry --print-ttl` (classes `gac:Registry`,
   `gac:Capability`, `gac:ResponseVariant`, `gac:CapabilityField`, `gac:EnumValue`,
   `gac:Dialect`, `gac:RefusalCode`, `gac:LawStep`, `gac:VocabularyEntry`, `gac:Limit` with
   scope, unit and source, and the typed `gac:Model`, `gac:ModelField`, `gac:ModelEnum`,
   `gac:ModelEnumValue`).
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
- `AshGraphLaw.Model.<Name>` structs (Lease, SignedLease, Receipt, Attestation, Plan, Action,
  PolicyEntry, PolicyOutcome; unknown keys kept in `:extra`), `AshGraphLaw.Model.Enums`, and
  `AshGraphLaw.Capability.Limits` (all/0 plus one accessor per limit)
- `documentation/reference/capabilities.md` and one reference page per operation
- `test/generated/capability_surface_test.exs` (pure, no wasm)

Gates compare against `gac:opCount`; no gate hardcodes the operation count.

## Typed models and limit scopes

| Model | Elixir module |
|---|---|
| Lease, SignedLease, Receipt, Attestation | `AshGraphLaw.Model.<Name>` (authority models, required by gate 150) |
| Plan, Action, PolicyEntry, PolicyOutcome | `AshGraphLaw.Model.<Name>` |

| Limit scope | Meaning |
|---|---|
| `abi` | request and structure bounds enforced at the JSON ABI |
| `hooks` | knowledge-hook rounds, firings and state size |
| `n3` | N3 reasoning iterations, derived facts, bytes and match steps |
| `plan` | plan size |
| `wasm` | outstanding wasm allocation |

## Gates

Ten registry gates (010-100), seven model and limit gates (110-170) and the coverage gate
`180_coverage_complete` (every op and native module has exactly one coverage row: GENERATED with
artifact or UNSUPPORTED(generator-capability) with reason and note). Gates 150 and 170 are inert
unless the graph declares a `gac:Model` or `gac:limitCount`. UNSUPPORTED(generator-capability):
signature verification, lease authorize, plan admit, policy validation, hook execution.

## Wiring

1. Vendor the pack into the consumer (`scripts/vendor_marketplace.sh`).
2. Import the registry RDF into the consumer `ontology.ttl` between the
   `BEGIN GENERATED-REGISTRY` and `END GENERATED-REGISTRY` markers, and add `gac:OpBinding`
   individuals.
3. List the pack under `[packs]` in the consumer `ggen.toml` and run `ggen sync`.

## Evidence boundary

Marketplace admission and ggen qualification (render plus gates) only. Semantic success is
PARTIAL_ALIVE at most; no execution authority is granted.
