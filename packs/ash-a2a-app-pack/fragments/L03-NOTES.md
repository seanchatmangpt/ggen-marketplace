# L03 notes: calculations

Coordinator seam. In `templates/resource.ex.tmpl`, add to `use Ash.Resource`:

```elixir
fragments: [{{ module_name }}.CalculationsL03]
```

Only for resources having `aap:calculation` (fragment file is emitted only for those, at
`lib/<appPath>/<resourceFile>_l03.ex`). Conditional guard: add a `calc_resources` query or emit
an empty fragment for all. Module-kind calcs emit `lib/<appPath>/calculations/<calcFile>.ex`.
The fragment module must compile before the resource (Elixir handles via compile deadlock-free
dependency tracking; fragments are required at resource compile time).

Do not also declare same-named attributes/calculations (gate L03_030).

## DSL options cited (deps/ash/lib/ash/resource/)

- calculate args name,type,calculation: dsl.ex:1756
- name/type/constraints/calculation/description/public?/sensitive?/load/allow_nil?/filterable?/sortable?:
  calculation/calculation.ex:29-110
- argument name,type,default,allow_nil?,allow_expr?,constraints: calculation/argument.ex:26-56
- builtin concat module `{Ash.Resource.Calculation.Concat, keys:, separator:}`: calculation/concat.ex:10-36
- behaviour init/load/calculate: concat.ex:9-39

## Known gaps

- Not modeled: async?, authorize?, field?, multitenancy (calculation.ex:39,73,114,124); `expression/2`
  callbacks in generated modules; module calcs other than coalesce; builtin calcs other than concat.
- Expression and constraints/default are raw Elixir text (not validated).
- Fragment is emitted via for_each only for resources with calculations; resource template wiring
  is coordinator work.
- `description` option in calculate do-block is `description` (calculation.ex:55).
