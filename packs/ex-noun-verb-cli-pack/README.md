# ex-noun-verb-cli-pack

Elixir-native noun-verb CLI framework port (ex_noun_verb_cli): declarative noun/verb dispatch, capability standing, command chaining/stdin extraction, generated via ggen from RDF rather than hand-authored.

Scaffolded by `ggen pack new ex-noun-verb-cli-pack` from `ggen-self-pack`
(`pack.toml`, `ontology.ttl`, `README.md` were generator output, not
hand-typed), then populated with this pack's real facts.

## Milestone 2: marketplace_cli Python-displacement evidence

This pack's original deliverable is not a Tera-templated generator -- it's
the concrete evidence that `ex_noun_verb_cli` can displace
`scripts/marketplace.py`. See `pack.toml`'s `description` for the full
charter. The real consumer app lives at `packages/marketplace-cli/`;
`ontology.ttl`'s `nvc:CliVerb` facts (`nvc:ValidateVerb`, `nvc:CatalogVerb`)
are read back for real by `queries/cli_verbs.rq` and
`queries/capability_shape.rq`, executed by that app's own test suite
(`test/marketplace_cli/cli_verbs_query_test.exs`).

Formerly named `noun-verb-cli-pack` (renamed -- a pack name repeating
"marketplace" is redundant with the pack already living in this marketplace).

## Extension: real capability-parity graph vs. clap-noun-verb

`ontology.ttl` also models, as real queryable data (not prose), exactly how
much of `~/clap-noun-verb` (the Rust original) `~/ex_noun_verb_cli` (the
Elixir port) actually implements -- every fact below is cited to something
real: a `file:line` range read and verified in full, a real design-spec
section, a real in-code `TODO`, or an explicitly verified absence.

### Classes

`nvc:Framework`, `nvc:Capability` (abstract; never instantiated directly --
see `gates/060_no_orphan_capability.rq`), its two leaf subclasses
`nvc:PortedCapability` / `nvc:DeferredCapability`, `nvc:CliVerb`,
`nvc:ExampleProgram`, `nvc:LocalPack`, `nvc:MarketplacePack`,
`nvc:OntologyClass`, `nvc:Citation`.

### The capability-standing split (55 individuals total)

- **10 `nvc:PortedCapability`** -- dispatch, JSON-by-default output,
  capability registry CRUD, dependency-closed topological ordering, `++`
  command chaining, `@-` raw stdin extraction, `@-::path` JSON-path stdin
  extraction, dual kebab-case/`snake_case` long-flag acceptance, the
  `Igniter.Mix.Task` adapter, and the escript adapter. Each cites a real
  `lib/ex_noun_verb_cli/**` `file:line` range in `~/ex_noun_verb_cli`.
- **8 `nvc:DeferredCapability`** -- `@{N.path}` cross-group step references
  (a real in-code TODO, not a spec non-goal), dynamic shell completions,
  `--introspect`, reflection-as-primary-registry, full frontier-feature
  parity, a real Hex.pm publish, and a concrete oxigraph/`ggen_igniter`-backed
  `GraphProvider` implementation -- each cites the real design-spec section
  in `docs/superpowers/specs/2026-09-11-ex-noun-verb-cli-design.md` (or the
  interface-only source file). One further deferred capability,
  Levenshtein-distance "did you mean?" suggestions (real in clap-noun-verb's
  `src/error.rs:45-82`), is cited as an **explicitly verified absence**: it
  appears in neither the design spec's non-goals section nor anywhere under
  `~/ex_noun_verb_cli/lib/` (`grep -rn -i levenshtein lib/` returns zero
  matches) -- a real gap, not a documented deferral.
- **10 `nvc:ExampleProgram`** individuals, one per real `.rs` file under
  `~/clap-noun-verb/examples/` that demonstrates a cited verb (or, for the
  one library-API-only example, `examples/capability_registry.rs`, cites
  the abstract `nvc:CapabilityRegistryCapability` it exercises instead).
- **9 new `nvc:CliVerb`** individuals (real noun/verb pairs from those
  examples) plus a real `nvc:filePath` added to the two pre-existing
  `nvc:CliVerb` individuals (`nvc:ValidateVerb`, `nvc:CatalogVerb`) pointing
  at their real `packages/marketplace-cli/lib/mix/tasks/*.ex` source.
- **1 `nvc:LocalPack`** (`~/clap-noun-verb/packs/clap-noun-verb-capability-pack`)
  and **12 `nvc:MarketplacePack`** individuals (the real six-pack split --
  schema/crate/routing/behavior/boundary/verification -- plus the 6 real
  adjunct/legacy packs already living in this marketplace:
  autonomic/telemetry/policies/specimen/zeroconfig/the deprecated
  `clap-noun-verb-pack`), each with its real `gates/*.rq` count verified via
  `find gates -iname '*.rq' | wc -l` at extension time.
- **3 sampled `nvc:OntologyClass`** individuals from `clap-noun-verb-schema-pack`'s
  real 14 `rdfs:Class` declarations (`cnv:Cli`, `cnv:Behavior`,
  `cnv:CustomBehavior`).

### Gates (`gates/*.rq`, ASK-true-means-violation, verified clean against `ontology.ttl`)

| Gate | Refuses |
|---|---|
| `010_ported_has_file_citation.rq` | a `PortedCapability` with no `filePath`+`lineRange` citation |
| `020_deferred_has_spec_citation.rq` | a `DeferredCapability` with no `specSection` citation |
| `030_example_demonstrates_verb.rq` | an `ExampleProgram` with neither a demonstrated verb nor a related capability |
| `040_verb_has_filepath.rq` | a `CliVerb` with no real `filePath` |
| `050_pack_gate_count_nonnegative.rq` | a pack with a missing or negative `packHasGateCount` |
| `060_no_orphan_capability.rq` | a bare `Capability` typed as neither leaf subclass |
| `070_citation_exclusivity.rq` | a `Citation` carrying both `filePath` and `specSection` |

### Queries (`queries/*.rq`)

`cli_verbs.rq` / `capability_shape.rq` are the original milestone-2 queries
(unchanged). Six new queries back one real `ExUnit` test each in
`packages/marketplace-cli/test/`, verified (via `rdflib`) to return exactly:
`ported-capabilities.rq` (10 rows), `deferred-capabilities.rq` (8 rows),
`example-verb-matrix.rq` (10 rows, includes `(CoreApiExample,
ServicesStatusVerb)`), `pack-gate-totals.rq` (`26`),
`marketplace-pack-catalog.rq` (12 rows), `capability-standing-split.rq`
(`ported=10, deferred=8`).

See `errc-tracker.md` for what's promotable from DEFERRED to PORTED next.
