# L08 notes: multitenancy

## Coordinator wiring

Resource fragments (one per aap:Resource with aap:multitenancy), module
`<Resource>.TenancyL08`, file `lib/<app_path>/<resource_file>_l08.ex`. Add to
templates/resource.ex.tmpl `use Ash.Resource`:

    fragments: [{{ module_name }}.TenancyL08]   # only for resources with aap:multitenancy

Domain fragment (module `<Domain>.MountsL08`, file `lib/<app_path>/<domain_file>_l08.ex`),
emitted only for domains with aap:mount. Add to `use Ash.Domain`:

    fragments: [{{ module_name }}.MountsL08]

Task store: `<store_module>.task_store("acme")` as an agent `:task_store` option.

Fragments need conditional emission; the coordinator should gate the `fragments:` line on
the SPARQL (`ASK`-style) existence of aap:multitenancy / aap:mount for that module.

## DSL options modelled

- multitenancy section: deps/ash/lib/ash/resource/dsl.ex:1787-1841 (strategy 1808,
  attribute 1815, global? 1821, parse_attribute 1828, tenant_from_attribute 1834).
- belongs_to: deps/ash/lib/ash/resource/relationships/belongs_to.ex (allow_nil? 90,
  attribute_public? 102, attribute_type 121; source_attribute via shared options, line 77).
- mount tenant: ash_a2a lib/ash_a2a/domain.ex:278-281 (`tenant`), struct at
  lib/ash_a2a/domain/mount.ex:28.

## Tenancy gap in TaskStore.Ash

lib/ash_a2a/task_store/ash.ex:6-9 stores only `namespace` (= ref); callbacks (`get/2`,
`put/2`, `list/2`...) take no tenant. Projection closes it by per-tenant namespace refs
(`<Store>.task_store(tenant)`). A true fix (TaskRow with multitenancy + tenant option on
the behaviour) needs an ash_a2a change; out of pack scope.

## Known gaps

- Fragment emission is unconditional per for_each row; resource.ex.tmpl must list the fragment.
- `of: Ash.Domain, extensions: [AshA2A]` in the domain fragment is unverified (no compile).
- A tenant FK declared both as aap:attribute and aap:relationship would duplicate the
  attribute; convention: declare it only as aap:relationship (gate 010 accepts either).
- Mounts for the same domain declared by another lane would collide on `transport do`.
- No tenant-aware actions (`multitenancy` on actions: `multitenancy :allow_global`, etc.) yet.
- Gate 040 cannot check mount-tenant uniqueness across mounts.
