# ERRC R2 wiring: domain, config, mix.exs seams

Standing: UNVERIFIED

Owned files: `templates/domain.ex.tmpl`, `templates/config.exs.tmpl`, `templates/mix.exs.tmpl`.
Nothing was rendered or compiled (no shell); all Tera/SPARQL below is unrun.

## domain.ex.tmpl

- One `domains` query (per-row `for_each`) now also returns `?vci ?has_l08 ?has_l10 ?has_l17`
  as the strings "true"/"false" (`BIND(IF(EXISTS ...))`), compared with `== "true"` in Tera.
- Fragment conditions mirror each lane's own emission filter exactly:
  - L08 `<Domain>.MountsL08`: domain has `aap:mount`.
  - L10 `<Domain>.L10`: any of domainDescription/Timeout/traceName/requireActor/authorize/
    allowUnregistered, or `aap:interfaceOfDomain` / `aap:mountOf` incident on the domain.
  - L17 `<Domain>.A2aL17`: `aap:a2aConfigured "true"`.
- When any fragment applies, `extensions: [AshA2A, AshA2A.Domain]` (L10/L17 notes require it).
  Otherwise the minimal demo output is unchanged: `use Ash.Domain, extensions: [AshA2A]`.
- `validate_config_inclusion?: false` is emitted when `aap:validateConfigInclusion "false"`.
- Fragment list is one per line with a trailing comma (valid Elixir, avoids Tera comma state).

## config.exs.tmpl

Lane config is inlined from the graph; no `import_config` anywhere.
- `ash_domains`: excludes `validateConfigInclusion "false"` domains (L10 semantics).
- `:agents`, repos (`ecto_repos`, dev/test repo settings, L09 mirror), Oban config and queues
  (L14 mirror, requires `aap:ObanConfig`), `:dispatch_hooks` (L17 mirror).
- Security profile: `aap:securityProfile` on the Project (optional) sets it in all envs;
  absent gives the previous `:legacy_compat` for dev/test only.

Still emitted by lanes but now unused (safe to stop emitting): `config/l09_data_layers.exs`,
`config/l10_ash.exs`, `config/L14_oban.exs`, `config/a2a_l17.exs`. If left emitted they are
harmless; they must not be imported (duplicate keys, last-wins).

## mix.exs.tmpl

Single `app` query returns feature flags; deps computed inline (no `deps_l09.exs` eval):
- ash_postgres / ash_sqlite: resource `aap:dataLayer` or `aap:Repo` repoKind.
- `:mnesia` in `extra_applications`: any resource `dataLayer "mnesia"`.
- oban: triggers, schedules, ObanConfig/Queue/DeliveryWorker. ash_oban: triggers/schedules.
- ash_state_machine: any `aap:stateMachine`. phoenix_pubsub: `aap:pubSub`, PubSubServer, A2ABridge.
- reactor (`>= 0.11.0`): aap:Reactor, ReactorCase, or any ppWorkflow.
- ash_pplan: lib dep when any ppWorkflow/ppProvider/ppPack/ppControlPlane/ppTarget; otherwise
  `only: :test` when an `aap:PlanCase` exists. Term from optional `aap:ashPPlanDep` on the
  Project (raw Elixir, e.g. `path: "/Users/sac/ash_pplan"` or `"~> 26.10"`), default `"~> 26.10"`.
- stream_data (`only: [:test, :dev]`): any `aap:CourtCase` or `aap:ShimCourt`.

## Residuals

1. `aap:ashPPlanDep` and `aap:securityProfile` are not declared in any ontology file (not
   owned here); queried as OPTIONAL, so absence is safe. Add them to the Project vocabulary.
2. `resource.ex.tmpl` is not owned here: resource `fragments:` (L08 TenancyL08, L09 DataLayer,
   L10, L11PubSub, L13 StateMachine, L14Oban, L17 A2aL17) and `simple_notifiers:` remain open.
3. Not wired by any template: application supervision (L09 repos/`start_mnesia`, L11
   `PubSubServer.children/0`, L14 `AshOban.config` + `{Oban, ...}`, L17 endpoint child),
   `config/runtime.exs` (L09 prod URLs), `.formatter.exs` `import_deps`.
4. L08 and L10 both can emit a `transport do mount` for one domain (collision noted in L08).
5. Version constraints (`ash_oban "~> 0.8 or ~> 0.9"`, `ash_state_machine "~> 0.2"`,
   `oban "~> 2.19"`, `ash_postgres "~> 2.0"`, `ash_sqlite "~> 0.2"`) are copied from
   ash_a2a/mix.exs and L09; unresolved against Hex.
6. `ash_oban`/`oban` flags do not detect Oban use implied only by `aap:ObanDeliveryWorker`
   when that class is absent from the graph.

## Unsupported / unverified Tera and SPARQL

- `or` between `==` comparisons inside `{% set x = ... %}`; fall back to nested `if` if rejected.
- `{% set %}` inside `{% if %}` is not used. `| default(value='"~> 26.10"')` with single-quoted
  literal containing double quotes, plus `| safe`.
- Empty-anchor `BIND(... EXISTS ...)` after OPTIONALs, `IF(BOUND(..) || EXISTS{..})`: relies on
  the ggen SPARQL engine supporting EXISTS in BIND and `?d` correlation inside EXISTS.
- Optional-column absence assumed to be undefined or empty; guarded with `default(value="")`.
- `for_each` row variables (`has_l08` etc.) assumed exposed at top level as `module_name` is.
