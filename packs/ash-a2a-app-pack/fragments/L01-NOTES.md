# L01 notes: Ash attributes in full

## Coordinator wiring

Add to the resource `use Ash.Resource` options (resource.ex.tmpl), only for resources that
have `aap:attrSpec` (the fragment file exists only then):

    fragments: [{{ module_name }}.L01Attributes]

Fragment file: `lib/<app_path>/<resource_file>_l01.ex`, module `<Resource>.L01Attributes`.
Enum modules: `lib/<app_path>/<enum_file>.ex` (independent, no wiring; needs compile order only).

## Seams and hazards

- Legacy `aap:attribute` edge is untouched; L01 uses `aap:attrSpec`. Gate L01_020 forbids
  name overlap. A resource with ONLY attrSpec PKs would fail gate 010 (it checks legacy
  aap:attribute primaryKey "true"): coordinator should extend 010 to accept
  `aap:attrSpec` with kind `*_primary_key` or `aap:isPrimaryKey "true"`.
- Spark fragment `fragments:` option requires the fragment module compiled first; Elixir
  resolves via compile-time dependency, fine in one project.
- Non-attribute kinds (timestamps, pk entities) emit name only: Ash hides all other options
  (attribute.ex:186,198,207,219,228); gate L01_030 enforces this.
- Expression-valued props (defaultExpr, updateDefaultExpr, constraints) are raw Elixir text.
  Regex/captures must be written as Elixir source. Description text is not escaped; no quotes.
- Booleans are string literals "true"/"false" (matches base ontology convention).

## DSL options covered (file:line in deps/ash/lib/ash/resource/)

attribute.ex: type 70, constraints 75, description 81, sensitive? 85, source 92,
select_by_default? 98, always_select? 105, primary_key? 112, allow_nil? 119, generated? 126,
writable? 133, public? 140, default 147, update_default 153, filterable? 157, sortable? 164,
match_other_defaults? 171. dsl.ex: attribute 36, create_timestamp 54, update_timestamp 79,
integer_primary_key 105, uuid_primary_key 133, uuid_v7_primary_key 159. Ash.Type.Enum
(type/enum.ex:73-80): bare, description-only, label-only, both. Array types:
`{:array, :t}`, `{:array, Module}`, enum arrays, `items:` via constraints.

## Known gaps

- `public?` is always emitted (default true); `public? false` requires explicit "false".
- Function-valued defaults as `{M,F,A}` tuples work only as raw text; no validation of Elixir.
- Embedded resource / union / struct / map `fields:` types are expressible only through
  aap:ashTypeModule + raw aap:constraints; no typed vocabulary (candidate for a later lane).
- Enum values with atoms needing quoting (e.g. dashes) not supported.
- `description` containing double quotes is unsafe.
- Nothing validated by compile or ggen run (no Bash).
