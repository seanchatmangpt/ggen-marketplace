# a2a-durability-pack

Packages the durability story of ash_a2a's A2A v1.0 surface as reusable,
consumer-facing manufacturing capital. Every surface grounds in a REAL
ash_a2a module (truth source: `/Users/sac/ash_a2a`, v1.0 drop; consumers
compile against hex `ash_a2a` at least that new) and cites exactly the
landed, zero-mock durability courts that witness it. Nothing here
synthesizes durability semantics.

## Surfaces (ontology individual -> real module -> lib path)

| Surface | Real module | Truth path | Witnessing court |
|---|---|---|---|
| `dur:PPlanProvider` | `AshA2A.Providers.PPlan` | `lib/ash_a2a/providers/pplan.ex` | `test/ash_a2a_pplan_durability_test.exs` (lane Y6) |
| `dur:EkvTaskStore` | `AshA2A.TaskStore.Ekv` | `lib/ash_a2a/task_store/ekv.ex` | `test/ash_a2a_v1_taskstore_durability_test.exs` (lane X9) |
| `dur:RestartContinuity` | `Runtime.continue/6` via `State.get_task/2` | `lib/ash_a2a/transport/runtime.ex` | lanes X9 (b) + Z8 (a)/(b): `test/ash_a2a_v1_multinode_continuity_test.exs` |
| `dur:StreamBoundary` | `Runtime.continue/6` `:task_in_progress` guard | `lib/ash_a2a/transport/runtime.ex` | lane Z8 (c) gap witness |

### What each surface claims

- **PPlanProvider** — async/multi-turn dispatch over the real ash_pplan
  durable stack: `dispatch/4` is start-or-adopt (idempotent by task id,
  never a duplicate execution), `resume/3` delivers the follow-up payload
  as a consume-once signal to the parked Await waiter (`:input_required`),
  `status/2` is read-only with the underlying run status in its detail map,
  `cancel/2` is claim-CAS. Honest: `:input_required` exists only for plans
  with an Await step; inputs bind at start only; `:auth_required`/`:rejected`
  are never produced; `:store` is a required host-owned opt (the provider
  starts no processes).
- **EkvTaskStore** — on-disk `AshA2A.Protocol.TaskStore`: tasks survive an
  agent crash/restart and a BEAM/node restart against the same `:data_dir`.
  At rest it strips `"a2a.auth"` and the node-local `:stream` key and
  deliberately persists `"ash_a2a.owner"` (ownership checks hold after
  restart; a continuation rebinds auth from the current call). Writes that
  EKV does not acknowledge raise `WriteError` — a non-durable success is
  structurally impossible. `:data_dir` is required, fail closed, no tmp-dir
  default.
- **RestartContinuity** — the proven continuity story: hard-kill store
  restart at the same `:data_dir`; a real two-node EKV cluster (one member
  on a separate OS-process `:peer` node) where a plug-created task
  replicates to the peer and a second agent continues it; fresh-agent
  read-through `get` (`State.get_task/2` falls through to the store on an
  in-memory miss — the exact path `Runtime.continue/6` takes). Honest hole,
  pinned as behavior: owner-scoped transport `tasks/list` pages the
  in-memory map only, so a fresh agent answers with a valid empty page even
  though the store holds the tasks.
- **StreamBoundary** — the honest gap, modeled as a gap: mid-flight streams
  are node-local and **cancelable, not resumable**. The persisted task is
  visible and resubscribable on a fresh agent; continuing it is refused
  typed (`:task_in_progress`); the honest close is the fresh agent's wire
  cancel, which publishes the terminal event that closes the resubscribed
  stream. Tracked upstream as GitHub issue #8 (named in
  `AshA2A.TaskStore.Ekv`'s moduledoc and the multinode court's gap
  witness). If any rendered artifact suggests streams survive agent loss,
  this pack is falsified.

## Gates

- `gates/010_surfaces.rq` — surface inventory (kind, truth module/path,
  wiring rows, config entry). Fail-closed companion:
  `verify/010_surfaces.unbound.rq` (missing `dur:kind`/`dur:truthModule`/
  `dur:truthPath`, or a store-kind surface without `dur:wiringModule`,
  refuses the pack; zero rows is the pass condition).
- `gates/020_capabilities.rq` — provider capability rows (name, produced
  A2A states, semantics). Companion: `verify/020_capabilities.unbound.rq`.
- `gates/030_court_citations.rq` — the court-citation inventory: one row
  per surface -> court edge. Companion `verify/030_court_citations.unbound.rq`
  refuses any surface with no `dur:citesCourt` edge and any citation that
  does not resolve to a `dur:Court` with a `dur:courtPath` — each
  individual must cite one of the three landed courts.
- `verify/cardinality.json` — predicate-anchored per-gate cardinality
  contracts whose blind spots are disjoint from the companions'.

## Templates

Rendered per consumer via ggen (specimen output paths under `tmp/`;
consumer replaces the specimen `dur:wiringModule` / `dur:wiringStoreName` /
`dur:wiringDataDir` rows with their own):

1. `templates/durable_task_store.ex.eex` -> a supervised durable-task-store
   wiring module: `child_spec/1` (Ekv `child_spec`, `:data_dir` defaulted
   to the wired value, never a tmp dir) and `task_store/1` (the
   `{AshA2A.TaskStore.Ekv, name}` tuple for the agent's `:task_store` opt).
2. `templates/pplan_provider_config.exs.eex` -> the pplan provider config
   snippet (`config :ash_a2a, :providers, [AshA2A.Providers.PPlan]`) with
   each capability, its produced A2A states, the honest gaps, and the
   consume-once resume hop as runnable comments.

## Falsifier

**Generated wiring boots a store that survives restart — the restart
court's procedure** (ported from `test/ash_a2a_v1_taskstore_durability_test.exs`
court (b)). The claim dies if any step fails:

1. Boot the generated wiring in a real supervision tree:
   `Supervisor.start_link([Wiring.child_spec(name: n, data_dir: d)], strategy: :one_for_one)`.
2. Write a task through the real store: `AshA2A.TaskStore.Ekv.put(n, task)`.
3. REAL restart: `Supervisor.terminate_child(sup, spec.id)` then
   `Supervisor.restart_child(sup, spec.id)` (aliveness is proven by the
   step-4 read, not a registration probe: EKV registers no process under
   `name`).
4. Rebooted store answers and re-reads at full fidelity:
   `{:ok, ^task} = AshA2A.TaskStore.Ekv.get(n, task.id)`.
5. Agent tier: a COLD `%AshA2A.Protocol.Agent.State{}` with only the store
   tuple finds the task via `State.get_task/2` (read-through).
6. At-rest redaction (court (c) tail): the raw persisted term and the
   on-disk bytes contain no `"a2a.auth"` token; `"ash_a2a.owner"` and
   unrelated keys are persisted verbatim.

The same procedure is embedded in the generated wiring module's moduledoc.
Provider-tier analogue (lane Y6): kill the pplan DETS store with
`Process.exit(store, :kill)`, reopen the same file, the parked
`:input_required` run answers `status/2` and `resume/3` completes it with no
step executed twice across the restart boundary.

### Measured verification (lane M11, 2026-10-04)

Subject: ggen-marketplace @ 384cd5e4, ash_a2a @ 5a84d88 (v1.0 drop, truth
modules as cited). Gates: 4 surfaces, 4 capability rows, 5 court-citation
rows; all three verify companions 0 rows (pass); anti-vacuity mutants all
detected (no-citation -> 4 rows, dangling citation -> 1, missing truthPath
-> 1, no-capabilities -> positive gate empties). Render + falsifier: both
templates rendered through EEx with the real gate-query bindings; generated
`MyApp.DurableTaskStore` compiled against ash_a2a's compiled v1.0 ebins
(read-only use); the restart procedure above ran end to end (legs 0-7,
rendered config parses; wiring compiles; store boots; raw-term redaction;
child terminate/restart at the same `:data_dir`; full-fidelity re-read;
cold read-through; on-disk byte scan: no token, no `a2a.auth` key, owner
persisted). Exit 0.

## Dependencies

- `a2a-v1-protocol-pack` (the A2A v1.0 protocol surface this durability
  story rides on).

## What this pack intentionally does NOT do

- No durability semantics synthesized: rendered artifacts delegate to the
  real `AshA2A.TaskStore.Ekv` / `AshA2A.Providers.PPlan` modules.
- No resumable-stream claim: `dur:StreamBoundary` is a gap witness with its
  tracking issue (GitHub #8), not a capability row.
- No mock courts: all witnesses are the landed zero-mock ExUnit courts in
  ash_a2a's test tree (real EKV instances, real DETS stores, real `:peer`
  OS-process nodes, real Bandit loopback listeners).
