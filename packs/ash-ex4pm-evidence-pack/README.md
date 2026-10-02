# ash-ex4pm-evidence-pack

Generalizes ash_pplan's evidence machinery -- machinery that exists in no other
marketplace pack -- into reusable, consumer-facing manufacturing capital.

## What it manufactures

Rendered per consumer `ex4ev:Emitter` row (the consumer's OWN Ash resource/action;
no ash_pplan module is ever embedded -- rendered modules are consumer-namespaced):

1. `{{ns}}.ProcessEvidence` + `.Event` -- the ProcessEvidence behaviour:
   receipts -> task_attempted / task_succeeded / task_failed OCEL events
   (attempted/succeeded pair per task; `failed` instead of `succeeded` at the
   failed task; tasks after a failure are never attempted), the pure OCEL 2.0
   JSON export, and the tamper-evident content digest (sha256 over
   term_to_binary({id, activity, attributes}); any attribute change flips it --
   LedgerOCEL.digest lineage).
2. `{{ns}}.Ex4pmAdapter` -- the guarded AshEx4pm adapter pattern: pure envelope
   build (`ash_ex4pm/1` wire shape), validate via the real
   `Ex4pm.OCEL.validate_envelope/1`, ingest via the real
   `Ex4pm.Stream.Ingest.ingest_envelope/2`, with the broadcaster OPT-IN
   via app env `:my_app, :broadcaster` (a module with `broadcast/1`), never a
   hard dependency.
3. `{{ns}}.RealtimeBridge` -- the bounded realtime seam: producers write via
   :persistent_term handoff, one bridge process drains into a capacity-bounded
   ETS ordered_set ring buffer with drop-oldest overflow (post-incident pattern
   after an unbounded broadcaster queued ~20k events and crashed the VM).
   Capacity via app env `:my_app, :bridge_capacity` (default 10_000).
4. `{{ns}}.EvidenceCourt` (test/) -- the Chicago-style evidence court: compiles
   the two rendered modules and the REAL Ex4pm (from EX4PM_ROOT, default
   ~/ex4pm), then runs fresh / duplicate / refusal / digest-tamper invariants,
   exit 1 on any violated invariant.

## Consumer integration steps

1. Copy the pack (or reference `--pack-dir`) and replace the specimen Emitter row
   in `ontology.ttl` with rows for YOUR Ash resources/actions
   (ex4ev:emitterResource/Action/Namespace/App).
2. Render:
   `MIX_BUILD_ROOT=_build-d6 mix ggen_igniter.sync --pack-dir <pack> --template <t> --ontology <pack>/ontology.ttl --out <consumer>/lib/...`
   per template (or a manifest run).
3. Add `:my_app` config:
   `config :my_app, broadcaster: nil` (opt-in) and
   `config :my_app, bridge_capacity: 10_000`.
4. Emit:
   `events = MyApp.Evidence.ProcessEvidence.events_from_receipt(receipt, subject, tasks: [...])`
   then `MyApp.Evidence.Ex4pmAdapter.validate(events, subject: subject)`
   and/or `ingest/2`; start `MyApp.Evidence.RealtimeBridge` in your supervisor
   and have your broadcaster call `MyApp.Evidence.RealtimeBridge.push/1`.
5. Court: `elixir packs/ash-ex4pm-evidence-pack/rendered/.../evidence_court.exs`
   with EX4PM_ROOT set to your ex4pm checkout.

## What it intentionally does NOT do

- No beam4pm coupling (gate 060 refuses any beam4pm literal in the ontology):
  the evidence plane is ex4pm-only, validated/ingested through the real
  Ex4pm.OCEL / Ex4pm.Stream.Ingest entry points.
- The broadcaster is opt-in via app env, never a hard dependency: with ex4pm,
  ash_ex4pm, or a broadcaster absent, everything still compiles and runs
  (guarded calls return `{:error, %{reason: :unsupported, detail: ...}}`).
- No producer embedding: no ash_pplan module is referenced by any rendered
  artifact; rendered modules belong to the consumer's namespace.
- No ingest-store admission: ingest goes through the real
  Ex4pm.Stream.Ingest.ingest_envelope/2 -- this pack does not reimplement or
  admit envelopes itself.
