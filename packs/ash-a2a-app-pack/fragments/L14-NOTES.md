# L14 notes: AshOban / Oban / Delivery.Oban

## Coordinator wiring

- Resource fragment (per resource having `aap:obTrigger` / `aap:obSchedule`), module
  `<ResourceModule>.L14Oban`, file `lib/<app_path>/<resource_file>_l14_oban.ex`. Add to
  `use Ash.Resource` in `templates/resource.ex.tmpl`:
  `fragments: [{{ module_name }}.L14Oban]` (conditional on the resource having L14 rows).
  The fragment declares `extensions: [AshOban]`; if Spark rejects fragment-supplied
  extensions, add `AshOban` to the resource `extensions: [AshA2A, AshOban]` instead.
- `config/L14_oban.exs`: add `import_config "L14_oban.exs"` to config/config.exs.
- mix.exs deps: `{:oban, "~> 2.19"}`, `{:ash_oban, "~> 0.x"}` (match /Users/sac/ash_a2a/deps).
- application.ex (not templated here): `AshOban.config(domains, base_oban_config)` and
  `{Oban, config}` in the supervision tree. Required for workers to run.
- Delivery worker file `lib/<app_path>/<worker_file>_l14.ex`; the handler module is host code.

## DSL options covered (ash_oban.ex)

- oban section: domain 723, list_tenants 728, shared_context 747, use_tenant_from_record? 771.
- trigger (205-500): name, action, where, sort, read_action, worker_read_action, queue,
  scheduler_queue, scheduler_cron (incl. false), worker_module_name, scheduler_module_name,
  max_attempts, max_scheduler_attempts, record_limit, stream_batch_size, stream_with, state,
  on_error, on_error_fails_job?, trigger_once?, lock_for_update?, worker_priority,
  scheduler_priority, log_errors?, log_final_error?, use_tenant_from_record?, shared_context,
  tags, backoff, timeout, action_input, extra_args, read_metadata, list_tenants,
  actor_persister, default_actor, worker_opts, debug?; chunks (size/timeout/by, 124-182).
- schedule (554-673): name, cron, action, queue, worker_module_name, max_attempts, state,
  priority, tags, action_input, list_tenants, actor_persister, default_actor, worker_opts,
  shared_context, debug?.
- Oban config: repo, engine, notifier, prefix, queues, Cron plugin, extra plugins, testing mode
  under `:test`, `config :ash_oban, pro?`.
- AshA2A.Delivery.Oban (/Users/sac/ash_a2a/lib/ash_a2a/delivery/oban.ex:86 `enqueue/3`,
  :138 `unique_opts/0`, :159 `perform_result/2`): worker with `unique:` default and
  result mapping. `perform/1` delegates to a host `Handler.run(args)`; no CommandBus
  signature was in the dispatch, so none is invented.
- ash_pplan oban.ex: gate 040 enforces what `AshPPlan.Oban` reads for
  `stable_worker_identity?` / `stable_scheduler_identity?` (oban.ex:430-437). Generated
  resources are therefore describable by `AshPPlan.Oban.describe_resource/1`.

## Gates

010 action refs declared; 020 schedule action type; 030 trigger action type; 040 stable
identity; 050 enums/ranges; 060 queue declared with limit; 070 chunks need Pro.

## Known gaps

- Resource template uses `Ash.DataLayer.Ets`; AshOban's `lock_for_update?`/keyset expectations
  assume a transactional data layer (AshPostgres). Needs a data-layer vocab lane.
- Triggered read actions must support keyset pagination (ash_oban.ex:367-372): the pack has no
  `pagination` action vocab; not gated.
- `where`, `sort`, `backoff` fn, `extra_args` fn are raw Elixir strings (unvalidated).
- `ash_oban` verifiers (verify_module_names, verify_use_tenant_from_record, verify_chunks)
  were not read; their rules are not gated beyond 040/070.
- `ash_oban.set_default_module_names`/signals workers (lib/signals/*) not modeled.
- `on_error`/`last_oban_attempt?` argument for schedules requires an action `argument`
  vocabulary the base ontology lacks.
- Tera `default` on absent OPTIONAL columns assumes ggen yields undefined (not empty) keys;
  both are handled by the `!= ""` guards.
