# L10 notes: code interfaces, domain config, mounts

Standing: UNVERIFIED

## Coordinator seams (exact lines)

Per resource with interfaces (module `<Resource>.L10`, file `lib/<app_path>/<resource_file>_l10.ex`):

    use Ash.Resource, domain: D, data_layer: Ash.DataLayer.Ets, extensions: [AshA2A],
      fragments: [<ResourceModule>.L10]

Per domain with config/mounts/domain-level interfaces (module `<Domain>.L10`, file
`lib/<app_path>/<domain_file>_l10.ex`; the fragment itself declares
`extensions: [AshA2A.Domain]`, spark/fragment.ex:10-14 pattern):

    use Ash.Domain, extensions: [AshA2A, AshA2A.Domain], fragments: [<DomainModule>.L10]

If `AshA2A.Domain` is not already in the host `extensions:` list, add it (the transport section
and the verifier require the host to carry the extension).

`validate_config_inclusion?: false` (domain/domain.ex:36-40) is a `use` option and cannot live in
a fragment. For domains with `aap:validateConfigInclusion "false"` the coordinator must emit
`use Ash.Domain, validate_config_inclusion?: false, ...`. L10_ash_domains_config omits them.

Config: `config/l10_ash.exs` holds the multi-domain `ash_domains` list. Add
`import_config "l10_ash.exs"` at the end of config/config.exs (key replaces the same key, so the
two lists must agree or L10's wins).

## Domain-level interfaces

Emitted as `resources do resource X do define ... end end` inside the domain fragment. The base
template's plain `resource(X)` merges with it: `Ash.Domain.Transformers.DedupResources`
(deps/ash/lib/ash/domain/transformers/dedup_resources.ex:22-42) concatenates `definitions`.

## DSL options covered (file:line, deps/ash/lib/ash)

- define: name, action, args (`?x` -> `{:optional, :x}`), get?, get_by, get_by_identity,
  not_found_error?, require_reference?, exclude_inputs, functions, namespace, default_options
  (raw term): resource/interface.ex:308-383.
- define_calculation: name, calculation, args (`arg:x`->`{:arg,:x}`, `ref:x`), exclude_inputs,
  namespace: resource/calculation_interface.ex:22-48.
- resource code_interface section: domain, define?, namespace: resource/dsl.ex:1141-1155.
- domain resource ref namespace, allow_unregistered?: domain/dsl.ex:151-155, 180-185.
- execution timeout/trace_name: domain/dsl.ex:39-51. authorization require_actor?/authorize:
  domain/dsl.ex:68-79. domain description: domain/dsl.ex:19-24.
- transport mount agent/path/binding/tenant/protocol_version: ash_a2a lib/ash_a2a/domain.ex:255-290.

## Files

- ontology.d/L10-code-interface.ttl, fixtures/L10-support.ttl
- templates/L10_resource_interface.ex.tmpl, L10_domain_config.ex.tmpl, L10_ash_domains_config.exs.tmpl
- gates/L10_010_interface_action_exists.rq, L10_020_interface_options.rq, L10_030_domain_config.rq

## Known gaps

- `allow` (mfa) on resources section, `custom_inputs` entity inside define, interface `args` for
  generic-action mappings beyond atoms, resource `code_interface` multiple-namespace validation.
- `get_by` fields are not checked against attributes (comma list not splittable in SPARQL).
- Tera features assumed: `starting_with` test, `trim_start_matches`, `split`, indexed `p[0]`;
  unverified until the coordinator renders. Row variable `timeout`/`description` shadow nothing.
- Domain fragment `description` is the `domain do` section; verify no clash with L-other lanes
  emitting `domain do` in their own fragments (Spark merges sections across fragments).
- Agents mounted must compile before the domain (VerifyMounts); coordinator ordering concern.
