# ash-pplan-chaos-pack

Generalizes ash_pplan's model-based chaos machinery — machinery that exists in
no other marketplace pack — into reusable, consumer-facing manufacturing
capital.

## What it manufactures

Rendered against ONE consumer `acp:Harness` row (the consumer's OWN
Generators/Harness/Invariants/Sabotage modules, generated-test namespace and
runs env var; no ash_pplan module is ever embedded):

1. One StreamData property suite per `acp:Invariant` row: a property with a
   fixed `initial_seed` (exact reproduction), `Harness.runs()` count, and an
   embedded anti-vacuity sabotage test (the check must refuse a corrupted
   observation).
2. One process-kill suite per `acp:KillPhase` row: kill (untrappable
   `Process.exit/2` `:kill`) at the declared boundary occurrence, heal, then
   EVERY invariant must hold after convergence, plus the anti-vacuity assertion
   that the kill fires and an unarmed scenario fires zero kills.

## Consumer integration steps

1. Copy the pack (or reference `--pack-dir`); replace the specimen
   `acp:Harness` row with YOUR harness modules/namespace/env, the specimen
   `acp:Invariant` rows with YOUR invariants, and the specimen `acp:KillPhase`
   rows with YOUR kill boundaries.
2. Render (per template, with `--for-each invariants` / `--for-each
   kill_phases`):
   `MIX_BUILD_ROOT=_build-x5 mix ggen_igniter.sync --pack-dir <pack> --template <pack>/templates/invariant_property.exs.eex --engine oxigraph --on-stale prune --out '<to-path>' --for-each invariants --manifest-dir <mf> --verify-cwd <project>`
3. Implement/keep YOUR `Generators`/`Harness`/`Invariants`/`Sabotage` modules —
   the suites alias them from the Harness row; the pack refuses to reimplement
   a consumer harness.
4. Run: `mix test test/<ns-path>/... --include chaos`.

## What it intentionally does NOT do

- No ash_pplan embedding: rendered suites alias CONSUMER modules; the specimen
  invariants (at_most_once, replay_identity, terminal_absorbing, no_lost_wakeup,
  standing_unique, cancel_sticky) are generic model-based chaos claims.
- No DO authority: the suites observe, they never actuate.
- No harness reimplementation: without the consumer's real harness modules the
  suites do not run — by design (Chicago: real collaborators, not fakes).
- Gates stay ORDER BY'd, no positional filter args, no literal `{%` anywhere in
  the pack (Tera-parse-safe), PREFIXes complete.
