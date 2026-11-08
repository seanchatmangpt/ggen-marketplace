# ash-pplan-igniter-pack

Manufactures the `mix ash_pplan.gen.workflow` Igniter task for ash_pplan from
a small ontology of facts. The ontology stores FACTS about the task (name,
module, group, shortdoc, example, options) in the canonical ggen_igniter
`igniter-task` vocabulary; the template
(`templates/gen_workflow_task.ex.eex`) derives all Elixir source from them —
the pack ships no hand-written Elixir.

## What It Projects

- `lib/mix/tasks/ash_pplan.gen.workflow.ex` — a `use Igniter.Mix.Task` module
  with two modes:
  - **scaffold**: generates a `Workflows.<Camel>` module containing an
    `AshPPlan.Workflow.Model` literal plus `@providers` / `@selection`
    attributes (code the `--add-provider` pass can rewrite). With
    `--with-resource`, it first composes the existing `ash.gen.resource`
    task via `Igniter.compose_task/4`.
  - `--add-provider`: semantically MODIFIES the existing workflow module by
    rewriting `@providers [...]` (prepend, deduped) and every value list in
    `@selection %{...}` (append, deduped) as AST — Sourceror parse, traverse,
    to_string; never string append. Typed refusals
    `REFUSED(ADD_PROVIDER_NO_PROVIDERS_LITERAL)` /
    `REFUSED(ADD_PROVIDER_NO_SELECTION_LITERAL)` when either literal is
    missing or the wrong shape.
- `qualification/igniter-fact-probe.txt` — a one-line fact probe rendered
  from the `ig:taskName` fact (template `qualification_probe.txt.tmpl`).

## Consumer Contract

Mix deps the projected task needs in the host app (`[consumer_contract]` in
`pack.toml`):

- `igniter` — `use Igniter.Mix.Task` and the whole `Igniter.*` API surface
  (31 call sites in the projected task);
- `sourceror` — `Sourceror.parse_string!/to_string` (2 call sites); brings
  `Rewrite` transitively for `Rewrite.Source.get/update` (2 call sites).

Peer context: the host app must provide `ash` + `ash_pplan` — the scaffolded
module aliases `AshPPlan.Workflow.Model`, and `--with-resource` composes
`ash.gen.resource`, which is an ash-provided task. The pack itself is a pack
project (no `ggen.toml` at its root); a consumer binds it by path:

```toml
[packs]
"ash-pplan-igniter-pack" = { path =
"../ggen-marketplace/packs/ash-pplan-igniter-pack" }
```

with the consumer's own `[ontology]`/`[templates]` using relative paths
(ggen refuses absolute paths). Deleting `igniter` or `sourceror` from the
host app is load-bearing-fatal: the projected task fails to compile
(undefined module `Igniter.Mix.Task` / `Sourceror`), which the anti-vacuity
flip in the qualification court proves by real compile.

## Gates

Two violation gates over the ontology (both must select zero rows):

- `gates/010_task.rq` — an `ig:Task` row missing ANY of
  taskName/module/group/shortdoc/example/moduledocBody refuses.
- `gates/020_options.rq` — an `ig:Option` row missing ANY of
  optionOf/optName/optType/optRequired/optHelp refuses.

## Qualification Court

Real-court, Chicago-style: a scratch consumer Mix project is manufactured in
a temp dir by the actual ggen runtime (`ggen sync run`), then compiled by the
real toolchain (`mix deps.get` + `mix compile`) with `igniter` + `sourceror`
resolvable from hex. Anti-vacuity flip: with `sourceror` removed, `mix
compile` must FAIL (the court must be able to flip from PASS to FAIL on a
real mutation, else it is vacuous). Absence of the toolchain would be a
typed UNVERIFIED, not a fake pass — mix/elixir were present this session
(elixir 1.19.5 / OTP 28).
