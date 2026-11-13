# L09 notes: data layers

Standing: UNVERIFIED

## Fragment seam

Per resource with `aap:dataLayer`, `templates/L09_data_layer_fragment.ex.tmpl` emits
`lib/<appPath>/<resourceFile>_l09.ex` defining `<Resource>.DataLayer`
(`use Spark.Dsl.Fragment, of: Ash.Resource, data_layer: <layer module>`).

Coordinator must add to the resource template's `use Ash.Resource` for resources that have
`aap:dataLayer`:

    fragments: [{{ module_name }}.DataLayer]

and drop the hardcoded `data_layer: Ash.DataLayer.Ets` for those resources (data_layer is a
single_extension_kind, ash resource.ex:19; a second source conflicts). Fallback if fragment
`data_layer:` is rejected: resource template emits `data_layer: <layer module>` itself (module
map: ets Ash.DataLayer.Ets, mnesia Ash.DataLayer.Mnesia, simple Ash.DataLayer.Simple, postgres
AshPostgres.DataLayer, sqlite AshSqlite.DataLayer) and the fragment drops the `data_layer:` opt
and keeps only the section.

Resources without `aap:dataLayer` get no fragment file; keep them out of `fragments:`.

## Coordinator wiring (other generated files)

- `deps_l09.exs`: mix.exs `deps: deps() ++ elem(Code.eval_file("deps_l09.exs"), 0)`.
- `aliases_l09.exs`: mix.exs `aliases: elem(Code.eval_file("aliases_l09.exs"), 0)`.
- mnesia: add `:mnesia` to `extra_applications`; call `<App>.DataLayerSetup.start_mnesia/0` at boot.
- `config/l09_data_layers.exs`: `import_config "l09_data_layers.exs"` end of config.exs.
- `config/l09_runtime.exs`: `import_config "l09_runtime.exs"` in config/runtime.exs (create if absent).
- `.formatter.exs`: `import_deps: [:ash_postgres]` / `[:ash_sqlite]` (shared file).
- Supervision: add repos (`<App>.DataLayerSetup.repos/0`) to the application supervisor.
- Migrations and `priv/resource_snapshots` are produced by `mix ash.codegen`, not by ggen.

## DSL options covered (file:line)

- Ets `ets do private?, table` : ash/lib/ash/data_layer/ets/ets.ex:11-38 (private? :25, table :31).
- Mnesia `mnesia do table` : ash/lib/ash/data_layer/mnesia/mnesia.ex:8-26; table creation via
  `Ash.DataLayer.Mnesia.start(domain, resources)` mnesia.ex:49-68.
- Simple: no section; `data_layer: Ash.DataLayer.Simple` is the Ash.Resource default (resource.ex:25).
- Fragment / data_layer single extension: ash/lib/ash/resource.ex:19.
- AshPostgres `postgres do table, schema, repo, migrate?, base_filter_sql, skip_unique_indexes,
  custom_indexes(index fields, name, unique, using, where, include, nulls_distinct),
  references(reference rel, on_delete, on_update, name, deferrable), check_constraints
  (check_constraint attr, name, check, message), custom_statements(statement up/down)`.
- AshSqlite `sqlite do table, repo, migrate?, base_filter_sql, strict?, custom_indexes, references`.
- Repo: `use AshPostgres.Repo, otp_app:` with `installed_extensions/0`, `min_pg_version/0`;
  `use AshSqlite.Repo, otp_app:`.

## Known gaps

- No ash_postgres / ash_sqlite source exists on this machine (searched ash_a2a deps, demo3 deps,
  gymact/paas, srve/platform, natfac/platform, zoela_phx); Postgres/SQLite options are modeled
  from AshPostgres 2.x / AshSqlite 0.2 knowledge, no file:line. Verify at first compile.
- Not modeled: polymorphic?, migration_types, migration_defaults, identity_wheres_to_sql,
  exclusion_constraint_names, foreign_key_names, storage_types, multitenancy migrations,
  Postgres custom_indexes `concurrently`, `prefix`, `message`; Ets `ets` persistence across
  restarts (not an Ash option); Mongo/other layers; ecto `Repo.init` tenants, `prefer_transaction?`.
- `references` need a relationship node; the shared ontology has no relationship vocab (another
  lane), so `aap:ofRelationship` is a free string.
- `.tmpl` autoescape behaviour unknown; SQL uses `| safe`. Index field expressions with non-
  identifier text emit as strings.
- Mnesia attributes: ash creates tables with `[:_pkey, :val]` itself (mnesia.ex:67).
