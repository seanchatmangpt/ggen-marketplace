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

## Extension 2: a real generation layer

Beyond documenting capability parity, this pack can generate a genuine,
compiling Elixir consumer of `~/ex_noun_verb_cli`'s real public API. This is
NOT a capability-parity survey of an existing app -- it is a code generator
for a *new* one, given only an RDF instance graph.

### The shape (`ontology.ttl`, "EXTENSION 2" section)

- `nvc:GeneratedCliProject` -- one per generatable project: `nvc:appName`,
  `nvc:moduleName`, `nvc:version`, `nvc:elixirVersion`,
  `nvc:exNounVerbCliVersion`, `nvc:description`, `nvc:hasVerb` (multi).
- `nvc:GeneratedVerb` (`rdfs:subClassOf nvc:CliVerb` -- reuses this pack's
  existing verb class rather than duplicating it) -- adds
  `nvc:handlerModule`/`nvc:handlerFunction`/`nvc:verbDescription`/
  `nvc:handlerBodyExpr`/`nvc:hasArgument` (multi) to the `nvc:noun`/`nvc:verb`
  facts `nvc:CliVerb` already carries.
- `nvc:GeneratedArgument` -- `nvc:argName`/`nvc:argType`/`nvc:argRequired`/
  `nvc:argOrder`, projecting directly into
  `ExNounVerbCli.Verb`'s real `info.schema`/`info.required` keyword-list
  shape (`lib/ex_noun_verb_cli/verb.ex:15-20`) and into the generated
  handler function's own parameter list, kept in the same order.

`nvc:handlerBodyExpr` is a real, honest, playground-authored Elixir
expression (e.g. `"x + y"`) -- a deliberate divergence from
`clap-noun-verb-crate-pack`'s `templates/custom_handlers.rs.tmpl`
`unless_exists: true` + `todo!(...)` stub convention: this pack's generated
projects are genuinely working CLIs end-to-end, not scaffolds.

### The playground instance (`playground/greet-cli.ttl`)

One real, complete `nvc:GeneratedCliProject` (`greet_cli`): noun `greet`
(verbs `hello`/`shout`, one required `name: :string` arg each) and noun
`math` (verbs `add`/`multiply`, two required `x:`/`y: :integer` args each) --
matching `~/ex_noun_verb_cli`'s own real `examples/calc/` proof-of-concept
(`ExNounVerbCli.Examples.Calc`/`.Registry`) in shape, extended with a second
noun and string-typed arguments.

### The templates (`templates/*.tmpl`, real Tera via `GgenIgniter.Render.TeraWasm`)

| Template | Emits | Real API it targets |
|---|---|---|
| `mix.exs.tmpl` | `mix.exs` | `escript: [main_module: ExNounVerbCli.Escript]` (real, `lib/ex_noun_verb_cli_escript.ex`) |
| `config.exs.tmpl` | `config/config.exs` | `config :ex_noun_verb_cli, registry: ...` (real, `ExNounVerbCli.Escript.main/1` resolves this key) |
| `registry.ex.tmpl` | `lib/<app>/registry.ex` | `use ExNounVerbCli.Registry.Generated, verbs: [...]` (real, `lib/ex_noun_verb_cli/registry/generated.ex`) |
| `handler_stub.ex.tmpl` | `lib/<app>/<noun>.ex`, one per noun, `unless_exists: true` | real handler functions, bodies from `nvc:handlerBodyExpr` |
| `README.md.tmpl` | `README.md` | build/run instructions for the generated project |

Known, disclosed limitation: templates use the `.tmpl` extension (matching
`clap-noun-verb-crate-pack`'s convention) rather than `.tera` --
`GgenIgniter.Render.TeraWasm.tera_template?/2`'s real dispatch predicate
(`lib/ggen_igniter/render/tera_wasm.ex:52-54`) only routes `.tera`-suffixed
paths through the WASM Tera engine automatically under a real
`mix ggen_igniter.sync` run. This pack's own `verify/render_check.exs` calls
`GgenIgniter.Render.TeraWasm.render/2` directly (bypassing that dispatch),
so the `.tmpl` extension does not block this pack's own real proof, but a
future `mix ggen_igniter.sync` integration would need either a rename to
`.tera` or an explicit `--engine`-style override -- not yet done, named here
rather than silently assumed.

### The real render proof (`verify/render_check.exs`)

```
cd ~/ggen_igniter
mix run <this pack>/verify/render_check.exs
```

Loads `playground/greet-cli.ttl` via `GgenIgniter.Ontology.load!/1`, parses
each template's real frontmatter via `GgenIgniter.Frontmatter.split_template/1`,
runs every named query via `GgenIgniter.Query.Oxigraph.run/2` (the real
oxigraph engine -- required for `ORDER BY` correctness, since the default
`sparql`-hex engine is documented to reverse `ORDER BY` results), pre-joins
each verb's `schema`/`required`/`params` strings in Elixir (documented
workaround for Tera's nested-loop `loop.last` conflation -- see
`templates/registry.ex.tmpl`'s own comment), renders both the `to:` path and
template body via `GgenIgniter.Render.TeraWasm.render/2` (the real WASM Tera
engine), writes every output under `examples/greet-cli/`, and validates every
generated `.ex`/`.exs` file with `Code.string_to_quoted!/1`.

Real output, verified 2026-09-11: 6 files written (5 Elixir + `README.md`),
all 5 Elixir files `QUOTED_OK`, `render_check: PASS`. The rendered files are
committed under `examples/greet-cli/` as proof, matching
`clap-noun-verb-zeroconfig-pack`'s own convention of committing its real
generated crate.

### Real `mix compile` (the ceiling, not just the floor)

`Code.string_to_quoted!/1` (above) is syntax validity -- the floor. A scratch
copy of `examples/greet-cli/` was actually compiled and run:

1. `{:ex_noun_verb_cli, "~> 26.9"}` (the committed, real Hex-style
   constraint) cannot resolve: `ex_noun_verb_cli` is not yet published to
   Hex.pm (`curl https://hex.pm/api/packages/ex_noun_verb_cli` -> 404,
   confirmed 2026-09-11; already a cited, disclosed deferral via
   `nvc:HexPublishCapability` in this pack's Extension 1 graph). The scratch
   copy's `mix.exs` overrides this ONE line to `{:ex_noun_verb_cli, path:
   "/Users/sac/ex_noun_verb_cli"}` -- an explicit, commented, scratch-only
   change, never applied to the committed `examples/greet-cli/mix.exs`.
2. That alone still failed: `ex_noun_verb_cli`'s own
   `lib/mix/tasks/ex_noun_verb_cli.ex` unconditionally `use`s
   `Igniter.Mix.Task`, but `mix.exs` declares `{:igniter, "~> 0.5", optional:
   true}` -- Mix's real semantics for `optional: true` only pull a dependency
   in when the TOP-LEVEL consuming application also declares it itself, so a
   bare path-dependency consumer with no `:igniter` of its own fails to
   compile `ex_noun_verb_cli` at all (`** (CompileError) ... module
   Igniter.Mix.Task is not loaded`). Adding `{:igniter, "~> 0.5"}` explicitly
   to the scratch copy's own deps closed this gap.
3. With both scratch-only additions, `mix deps.get` and
   `mix compile --warnings-as-errors` both succeeded for real (`Generated
   greet_cli app`), then `mix escript.build` produced a real `./greet_cli`
   binary, which was actually run for all four verbs plus one deliberately
   unregistered verb:

   | Command | Real output | Exit |
   |---|---|---|
   | `./greet_cli greet hello --name Sean` | `{"result":"Hello, Sean!","status":"ok"}` | 0 |
   | `./greet_cli greet shout --name Sean` | `{"result":"HELLO, SEAN!","status":"ok"}` | 0 |
   | `./greet_cli math add --x 2 --y 3` | `{"result":5,"status":"ok"}` | 0 |
   | `./greet_cli math multiply --x 4 --y 5` | `{"result":20,"status":"ok"}` | 0 |
   | `./greet_cli math divide --x 4 --y 5` | `{"error":{"code":"unknown_verb",...},"status":"error"}` | 1 |

This is a genuinely working, generated, end-to-end CLI -- not merely
syntactically valid source.

### Gates (`gates/080`-`083`, new -- ASK-true-means-violation, same convention as `gates/010`-`070`)

| Gate | Refuses |
|---|---|
| `080_generated_project_exactly_one.rq` | zero or more than one `nvc:GeneratedCliProject` per graph |
| `081_generated_verb_required_props.rq` | a `nvc:GeneratedVerb` missing `noun`/`verb`/`handlerModule`/`handlerFunction`/`handlerBodyExpr` |
| `082_argument_order_dense_unique.rq` | two `nvc:GeneratedArgument`s of the same verb sharing an `nvc:argOrder` |
| `083_no_duplicate_noun_verb.rq` | two `nvc:GeneratedVerb`s sharing the same `(noun, verb)` pair |

Verified 2026-09-11 via `rdflib`, both clean AND falsification-hardened
(never asserted vacuously true): each gate is `ASK=False` against the real
`playground/greet-cli.ttl`, AND a real, independent one-fact mutation per
gate flips it to `ASK=True`:

| Gate | Mutation applied | Result |
|---|---|---|
| 080 | add a second `nvc:GeneratedCliProject` individual | `True` (caught) |
| 081 | remove `nvc:GreetHelloVerb`'s `nvc:handlerBodyExpr` | `True` (caught) |
| 082 | set `nvc:MathAddYArg`'s `nvc:argOrder` to `0` (colliding with `nvc:MathAddXArg`) | `True` (caught) |
| 083 | add a second `nvc:GeneratedVerb` also typed `(noun="math", verb="add")` | `True` (caught) |

Renumbered from 070-073 (the design's original suggestion) to 080-083 to
avoid colliding with this pack's own pre-existing
`gates/070_citation_exclusivity.rq`.

Gate-running note: these 4 gates (like `gates/010`-`070` above) are ASK
queries, verified via `rdflib`'s real ASK semantics -- NOT run through
`ggen_igniter`'s own `GgenIgniter.GateVerify`/`mix ggen_igniter.doctor`
machinery, which treats every `gates/*.rq` as a plain `SELECT` and uses a
"returns >= 1 row" pass convention. Real, confirmed incompatibility:
`GgenIgniter.Query.Oxigraph.run/2` raises `RuntimeError`
(`OxigraphEngineError::NotSelectQuery`) on a real ASK query, and the default
`GgenIgniter.Query.run/2` silently mis-evaluates one instead of raising
(returns the WHERE-clause bindings as SELECT-shaped rows, not a boolean --
see `lib/ggen_igniter/query.ex`'s own moduledoc). This is the same
gate-verification approach this pack's `errc-tracker.md` already used for
`gates/010`-`070`, not a new inconsistency introduced by this extension.
