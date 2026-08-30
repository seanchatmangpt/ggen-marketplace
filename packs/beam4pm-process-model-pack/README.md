# beam4pm-process-model-pack

Projects an admitted `bpm:RecordType` graph into real, compiling Erlang and Elixir
type/struct definitions -- with constructors that refuse construction when a required
field is absent, and Chicago-style (no mocks) unit tests that exercise those real
generated constructors.

This pack ships templates and vocabulary only. It declares no `bpm:RecordType` or
`bpm:Field` individuals of its own -- the actual process-mining record definitions
(OCEL 2.0 events and objects, directly-follows edges, Petri net places, transitions
and arcs, and conformance-checking alignment moves) are admitted instance data
supplied by the consuming project's own `ontology.ttl` (e.g. `beam4pm`), using the
`bpm:` vocabulary declared in this pack's own `ontology.ttl`.

## What it generates

From every admitted `bpm:RecordType` in the consumer's graph, this pack's 11 templates
each run a `records` + `fields` SPARQL query pair over the merged graph and render:

- `templates/beam4pm_types.erl.tmpl` -> `src/beam4pm_types.erl` --
  one `-record/1` + `-type/0` declaration (plus a single `-export_type` list) and one
  `new_<record_name>/1` constructor per record type, returning `{ok, #record{}}` or
  `{error, {missing_field, atom()}}`.
- `templates/beam4pm_types_tests.erl.tmpl` -> `test/beam4pm_types_tests.erl`
  -- real EUnit tests calling those constructors (one ok-path test and one
  missing-required-field test per record type).
- `templates/beam4pm_types.ex.tmpl` -> `lib/beam4pm_types.ex` -- one
  `BeamPM.Types.<RecordName>` struct module per record type (all in one file), each
  with a `new/1` constructor returning `{:ok, t()}` or `{:error, {:missing_field, atom()}}`.
- `templates/beam4pm_types_test.exs.tmpl` -> `test/beam4pm_types_test.exs`
  -- real ExUnit tests calling those constructors.
- `templates/beam4pm_types_test_helper.exs.tmpl` -> `test/test_helper.exs`
  -- the `ExUnit.start()` bootstrap Mix requires when `test_paths` is set explicitly.
- `templates/beam4pm_types.schema.json.tmpl` -> `schema/beam4pm_types.schema.json`
  -- a draft-07 JSON Schema document, one sub-schema per record type, for wire-format
  documentation independent of either language projection.
- `templates/beam4pm_types_reference.md.tmpl` -> `docs/reference/beam4pm_types_reference.md`
  -- a generated Markdown reference table (one section per record, one row per field).
- `templates/beam4pm_types_manifest.erl.tmpl` / `.ex.tmpl` -> `src/beam4pm_types_manifest.erl`
  and `lib/beam4pm_types_manifest.ex` -- pure reflection modules
  (`record_names/0`, `fields/1`) with no dependency on the `-record`/`defstruct`
  definitions above, so they render safely regardless of which records exist.
- `templates/beam4pm_types_manifest_tests.erl.tmpl` / `_test.exs.tmpl` -- real
  EUnit/ExUnit tests for those two reflection modules.
- `templates/beam4pm_precision.{erl,ex}.tmpl` + `_tests.erl.tmpl`/`_test.exs.tmpl` --
  ETC (Escaping-edge Trace Conformance) precision over a `dfg_edge` model and a
  `log_trace`, structurally adapted from ex4pm's real `Ex4pmEngine.ETCPrecision`
  (see the module's own moduledoc for the full derivation and the rejected
  alternative mappings considered).
- `igniter/templates/beam4pm_receipt_chain.ex.eex` + `_test.exs.eex` (ggen_igniter,
  not Tera) -- hash-chained `beam4pm-brce/v1` receipts, adapted from ex4pm's real
  `Ex4pm.Evidence.Replay.Chain`; purely additive (opt-in via `actuation_opts[:chain_id]`,
  automatically scoped per-process by `BeamPM.ProcessGovernor`).
- `igniter/templates/beam4pm_rf1_dfg.ex.eex` + `_test.exs.eex`, `beam4pm_rf2_conformance.ex.eex`
  + `_test.exs.eex`, `beam4pm_rf3_ocel.ex.eex` + `_test.exs.eex` (ggen_igniter, not Tera) --
  Reactor-orchestrated, real-subprocess-oracle-backed validation of rust4pm's
  (`process_mining` crate) documented function surface against canonical wasm4pm
  datasets: RF1 = `discover_dfg`, RF2 = Alpha+++ discovery + `align_variants` +
  `compute_fitness` (real 1434-trace `receipt.xes`), RF3 = OCEL 2.0 slim bindings
  (`bindings::slim_link_ocel`, `SlimLinkedOCEL`) including three real adversarial
  fixtures from `wasm4pm/fixtures/negative/` (n05, n13, n14). Every scenario has a
  named `compensate/2` falsify path writing a typed refusal receipt. RF1/RF3 are
  fully static templates (oracle-observed constants baked in from real runs, like
  `beam4pm_receipt_chain.ex.eex`); RF2's template genuinely queries
  `rf2:ConformanceStream` (`igniter/queries/rf2_spec.rq`) for the oracle/wire-op/
  dataset/module identity via real oxigraph. Adapted from the
  rust4pm-Reactor-validation swarm, independently re-verified (clean cargo
  rebuilds, fresh `mix test`) before integration.
- `templates/beam4pm_pi3_falsifier_test.exs.tmpl` + `_tests.erl.tmpl` -- PI3
  (process inference) falsifier court for the real `BeamPM.Discovery` pipeline:
  proves a known, hand-designed branching process (`receive_order ->
  validate_order -> [ship_order | reject_order] -> close_order`) is recovered
  as an exact DFG edge-set match, AND that false adjacency -- event pairs
  timestamp-adjacent in the raw, unpartitioned stream but belonging to
  different cases -- is never promoted into a spurious edge, including under
  concurrent-interleaved unrelated processes, shared activity-name vocabulary
  across those processes, and a 300-single-event-fragment flood stress case.
  21 hand-designed adversarial tests per language, order-independence checked
  via multiple permutations at up to 4000-event scale, and a non-vacuousness
  check (deliberately removing a real edge from the expected set to confirm
  the suite actually fails when the code would be wrong).

`to:` paths in every template above are relative to the **consuming project's root**
(e.g. `src/...`, not `../../src/...`) -- ggen resolves
`to:` against the project root regardless of where the template file itself lives inside
a vendored pack, and refuses (`FM-WRITE-002`) any `to:` value containing a `../`
traversal component.

Field types map from the closed `bpm:fieldType` enum to Erlang and Elixir types
identically in both languages' templates:

| `bpm:fieldType` | Erlang       | Elixir                                    |
|-----------------|--------------|--------------------------------------------|
| `string`        | `binary()`   | `String.t()`                                |
| `integer`       | `integer()`  | `integer()`                                 |
| `float`         | `float()`    | `float()`                                   |
| `boolean`       | `boolean()`  | `boolean()`                                 |
| `datetime`      | `binary()`   | `String.t()` (ISO8601 string on the wire)   |
| `atom`          | `atom()`     | `atom()`                                    |
| `list_string`   | `[binary()]` | `[String.t()]`                              |
| `map`           | `map()`      | `map()`                                     |

`bpm:fieldRequired` must be the plain string literal `"true"` or `"false"` (not an
`^^xsd:boolean`-typed literal) -- the templates compare it as a string, and this keeps
the comparison independent of how any particular SPARQL engine happens to serialize a
typed boolean literal.

## Where to look

- `templates/beam4pm_types.erl.tmpl`, `templates/beam4pm_types_tests.erl.tmpl` -- the
  Erlang struct/constructor side.
- `templates/beam4pm_types.ex.tmpl`, `templates/beam4pm_types_test.exs.tmpl`,
  `templates/beam4pm_types_test_helper.exs.tmpl` -- the Elixir struct/constructor side.
- `templates/beam4pm_types_manifest.erl.tmpl` / `.ex.tmpl` and their `_tests`/`_test`
  siblings -- the pure-reflection manifest modules, both languages.
- `templates/beam4pm_types.schema.json.tmpl` -- the generated JSON Schema document.
- `templates/beam4pm_types_reference.md.tmpl` -- the generated Markdown reference doc.
- `gates/010_required.rq` -- refuses any `bpm:RecordType`/`bpm:Field` missing a
  required property.
- `gates/020_field_type_enum.rq` -- refuses any `bpm:fieldType` outside the closed
  8-value enum.
- `ontology.ttl` -- the `bpm:` vocabulary itself (`bpm:RecordType`, `bpm:Field`, and
  their properties); no record-type individuals.

## Composing this pack

Add the real record-type instance data (OCEL events/objects, Petri net places,
transitions and arcs, directly-follows edges, alignment moves, etc.) to the
consuming project's own `ontology.ttl` using the `bpm:` vocabulary above, reference
this pack by path from that project's `ggen.toml` `[packs]` table, and run
`ggen sync run`. See `beam4pm`'s `ontology.ttl` and `ggen.toml` for a real, working
example consumer.
