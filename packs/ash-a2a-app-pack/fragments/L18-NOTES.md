# L18 notes: Spark custom DSL from TTL

Standing: UNVERIFIED

## Seam (coordinator)

Add to the Resource `use Ash.Resource` line of every resource that has `aap:sparkInstance`:

    fragments: [Demo.Ticket.SparkL18]

Generic form: `fragments: [<resource module_name>.SparkL18]`. The fragment itself declares
`extensions: [<ext module>]`, so no `extensions:` edit is needed on the resource.
Compile order is handled by Elixir (fragment requires extension module, which requires
Persist/Verify); all emitted into `lib/<appPath>/`.

Optional: merge `.formatter_l18.exs` into `.formatter.exs` as
`spark_locals_without_parens: Code.eval_file(".formatter_l18.exs") |> elem(0)` and add it to
`locals_without_parens` and the export list.

## Files per extension / resource

- `lib/<appPath>/<extFile>.ex` extension + entity struct modules (extension.ex.tmpl of ash-extension-pack
  is the package route; this is the in-app route, same Spark grammar: entity.ex name/target/args/identifier/schema/describe,
  section.ex name/describe/schema/entities, extension.ex sections/transformers/verifiers).
- `<extFile>_info.ex` Spark.InfoGenerator (info_generator.ex:23) + `summary/1`.
- `<extFile>_persist.ex` transformer persisting section counts (transformer.ex:88).
- `<extFile>_verify.ex` verifier: minEntities, uniqueField (verifier.ex:18; DslError).
- `<resourceFile>_l18.ex` fragment applying instances.
- `.formatter_l18.exs`, `docs/L18_spark_cheat_sheet.md`.

## Known gaps

- No nested entities, entity-level `singleton_entity_keys`, section `top_level?`, `imports`, `deprecations`,
  `links`, `examples`, `auto_set_fields`, `transform`, `no_depend_modules`, `recursive_as`, or `hide`.
- Transformer ordering (`before?/after?`) not modelled; instances support Ash.Resource targets only.
- Types are raw Elixir text; the gate does not parse them. Multiple instances of one entity in one
  section render one `section do ... end` block each (legal, Spark merges).
- Section-level instance options (section schema values) are not instantiable.
- Template syntax (`set_global` inside for loops, `filter(attribute=...)` on optional columns) unverified in ggen 26.11.5.
- Fixture lacks `aap:Attribute`/primary key facts; resource gate 010 may flag it when merged with the real graph.
