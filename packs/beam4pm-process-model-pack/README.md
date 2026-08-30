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

From every admitted `bpm:RecordType` in the consumer's graph, this pack's four
templates each run a `records` + `fields` SPARQL query pair over the merged graph and
render:

- `templates/beam4pm_types.erl.tmpl` -> `generated/erlang/src/beam4pm_types.erl` --
  one `-record/1` + `-type/0` declaration and one `new_<record_name>/1` constructor
  per record type, returning `{ok, #record{}}` or `{error, {missing_field, atom()}}`.
- `templates/beam4pm_types_tests.erl.tmpl` -> `generated/erlang/test/beam4pm_types_tests.erl`
  -- real EUnit tests calling those constructors (one ok-path test and one
  missing-required-field test per record type).
- `templates/beam4pm_types.ex.tmpl` -> `generated/elixir/lib/beam4pm_types.ex` -- one
  `BeamPM.Types.<RecordName>` struct module per record type (all in one file), each
  with a `new/1` constructor returning `{:ok, t()}` or `{:error, {:missing_field, atom()}}`.
- `templates/beam4pm_types_test.exs.tmpl` -> `generated/elixir/test/beam4pm_types_test.exs`
  -- real ExUnit tests calling those constructors.

The `to:` paths above are relative to this pack's own `templates/` directory
(`../../generated/...`), which resolves to `<consumer-project-root>/generated/...` when
this pack is vendored at `<consumer-project-root>/vendor/ggen-marketplace/packs/beam4pm-process-model-pack/`.

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
  Erlang side.
- `templates/beam4pm_types.ex.tmpl`, `templates/beam4pm_types_test.exs.tmpl` -- the
  Elixir side.
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
