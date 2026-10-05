# Falsifier receipt -- a2a-hex-migration-pack v0.1.0

Falsifier (pack contract): "the generated migration task runs on a scratch
consumer and its grep sweep reports zero A2A. refs."

## Run (2026-10-05, ggen 26.9.28, Elixir 1.19.5 / OTP 28)

- Subject: template rendered by the real ggen sync pipeline
  (`ggen sync run`, frontmatter projection; graph_hash_hex
  `ed68ef72f32a4f95c55b725fbe309daf7b588e0d1612878729441e1a84c48c33`)
  into a scratch Mix consumer (/tmp/ahm_consumer2.TnvS-shape, re-created per
  run) holding `{:a2a, "~> 0.2"}`, a bare `alias A2A`, and 9 bare `A2A.`
  refs across lib/ test/ config/ (baseline grep count: 9 + 1 alias + 1 dep).
- Command: `mix a2a_hex_migrate` (plain Mix.Task branch; Igniter not loaded).
- Observed: dep tuple removed (printed `removed dep: {:a2a, "~> 0.2"}`), 9
  verified table renames applied across 3 consumer files, wire-shape delta
  checklist (4 deltas) and step list printed, final sweep: PASS --
  zero A2A. refs, zero {:a2a, ...} deps.
- Post-state: bare-A2A. grep over lib/ test/ config/ mix.exs excluding the
  engine file = 0; `{:a2a` in mix.exs = 0; engine table intact (9 rows).
- Idempotence (engine-level, run directly): second pass over the migrated
  tree -> 0 residual rows, all 5 candidate files no-op rewrites.

## Known limits (disclosed, not claimed)

- The scratch consumer does not pin ash_a2a 26.10.3, so after migration the
  scratch tree itself no longer compiles (migrated refs need AshA2A.Protocol.*)
  and a second `mix a2a_hex_migrate` cannot recompile the project. Engine-level
  idempotence is proven instead (above). A full post-migration compile court
  requires a consumer that pins the new ash_a2a.
- The Igniter.Mix.Task branch is rendered and compiles only when Igniter is a
  dependency; the falsifier environment had no Igniter, so that branch is
  unqualified. The plain Mix.Task branch carries the same rewrite core.
- The engine file excludes itself from rewriting and sweeping (its literals
  ARE the verified table and the checklist); the guide's raw `grep -rn 'A2A\.'`
  therefore still matches the engine file's table and checklist text after
  migration. The precise pass gate is the task's own word-boundary sweep,
  which is what "zero A2A. refs" is measured on here.
