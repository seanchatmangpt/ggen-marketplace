# L15 Reactor notes

Standing: UNVERIFIED (no ggen run, no compile; coordinator sync is the court)

## Seam (coordinator action)

Reactors are standalone modules (no resource seam). Resource side is one Spark fragment per
resource that declares `aap:reactorFragment`. For fixture resource `Demo.Desk.Ticket` add to
templates/resource.ex.tmpl `use Ash.Resource` options:

    fragments: [Demo.Desk.TicketReactorActions]

(general form: `fragments: [<aap:reactorFragment value>]`; fragment declares
`extensions: [AshA2A]`, spark/lib/spark/dsl/fragment.ex:14). The fragment owns the generic
action and its a2a skill, so the resource's own `aap:action`/`aap:skill` edges must not
also declare them (L15 uses `aap:reactorAction`, which resource.ex.tmpl ignores).
If resource.ex.tmpl cannot take `fragments:`, the fragment module is still a valid standalone
file; the resource must list it.

Compile order: generated Reactor modules reference resources; resources reference the
fragment, whose action `run` references the Implementation, which references the Reactor.
Only runtime references, no compile-time cycle (Reactor steps name resources as atoms via
no_depend_modules, ash/lib/ash/reactor/dsl/create.ex:82).

## Files

- ontology.d/L15-reactor.ttl
- templates/L15_reactor.ex.tmpl (per reactor; recursive `self::step` macro)
- templates/L15_step_module.ex.tmpl (generated Reactor.Step impls; run/compensate/undo)
- templates/L15_reactor_action_impl.ex.tmpl (Ash generic-action Implementation running Reactor.run/4)
- templates/L15_reactor_fragment.ex.tmpl (generic action + a2a skill fragment)
- gates/L15_010 cycles, 020 undeclared deps, 030 effect compensation, 040 structure
- fixtures/L15-reactor.ttl

## Reuse of ash-extension-pack

Step-module shape mirrors reactor_step.ex.tmpl (run/3, compensate/4 only when declared) and
adds undo/4; ordered steps / wait_for / return mirror queries/reactor_steps.rq and
040_reactor_step_graph_contract.rq. The aex: vocabulary is not imported (different
namespace, spec-scoped); aap: facts are the source here. Bridge if wanted: CONSTRUCT
aap:ReactorStep from aex:ReactorStep (stepName, stepModule, stepWaitFor, stepHasCompensate).

## DSL options covered (file:line under /Users/sac/ash_a2a/deps)

- Reactor top: return dsl.ex:23; middlewares middleware.ex:30; input input.ex:52 (+transform :42-50)
- step: name/impl step.ex:81, description :98, max_retries :140, async? :148
- argument: argument.ex:194; templates input/result/value/element :59,:100,:127,:158; path; transform :220
- wait_for wait_for.ex:34
- compose: compose.ex:56,:80, allow_async? :87, async? :95, support_undo? :103
- map: map.ex:145 source, :152 return, :130 batch_size, :122 allow_async?, :159 strict_ordering?
- switch: switch.ex:131 on; matches? predicate :52; default :76; branch return :66
- around: around.ex:44 (fun supplied as raw `fun ...` aap:stepOpt, :67), allow_async? :74
- collect: collect.ex:54 (transform via aap:stepOpt); flunk: flunk.ex:57 message
- Ash steps create/update/destroy/read_one/read/action/bulk_*: args name/resource/action
  action.ex:64; shared options action.ex:83-141 (async?, authorize?, description, undo,
  undo_action); initial create.ex:100/update.ex:96/bulk_create.ex:176; upsert? create.ex:110,
  upsert_identity :105; fail_on_not_found? read_one.ex:84; read_action bulk_create.ex:203;
  inputs inputs.ex:45; actor actor.ex:28; tenant (tenant.ex)
- transaction: transaction.ex:49 args, resources :64, return :71, timeout :78
- generic action running a reactor: implementation.ex:5-60; Reactor.run options reactor.ex:152-176
- a2a skill on that action: ash_a2a dsl.ex:188-197, lease_required? :90, on_cancel :61

Anything not typed goes through `aap:stepOpt` (one raw option line per value), e.g.
`return_records? true`, `notify? true`, `transform &Mod.f/1`, `fun &Mod.f/4`.

## Known gaps

1. `where`/`guard` (reactor guards, where.ex/guard.ex) not modeled: guard captures only via stepOpt
   cannot express nested `guards` entities reliably.
2. `inputs` per-binding transform (inputs.ex:66) and actor/tenant `transform` ignored.
3. `group`, `debug`, `recurse`, `template` entities, `load`/`context` Ash sub-entities
   (action_load.ex, context.ex), `change` step (change.ex) not modeled.
4. Fragments only cover generic actions; bulk undo generic-action contract (bulk_create.ex:119)
   not checked by a gate.
5. Reactor description is moduledoc only (no `description` DSL emission).
6. Macro recursion (`self::step`) in Tera is untested here; if the engine rejects it, flatten to
   depth-2 loops (containers: map/around/transaction; switch branches).
7. Gate 030 treats any enclosing transaction as compensating; it does not verify the
   transaction's resources include the step's resource.
8. Gate 040 cannot check that a step `aap:stepImpl` module exists (external module).
9. Skill gate: existing 020_skill_targets_action.rq ignores `aap:reactorSkill`; the fragment
   action always exists by construction.
