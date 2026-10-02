# ash-pplan-store-conformance-pack

Generalizes ash_pplan's generated Store-conformance machinery — machinery that
exists in no other marketplace pack — into reusable, consumer-facing
manufacturing capital.

## What it manufactures

Rendered per consumer `scb:Target` row (the consumer's OWN behaviour module,
suite namespace, boot/start bodies; no ash_pplan module is ever embedded):

1. `{{suiteModule}}` — the generated ExUnit conformance suite: one test per
   `scb:Law` against any implementation of the consumer behaviour
   (`use Suite, store: M, start: fun`), a `run/2` returning
   `[{law_id, :ok | {:error, e}}]` for courts, a render-time coverage refusal
   (a callback covered by no law refuses the whole render), and the per-law
   crash-isolated runner (each law runs in an unlinked child process so a
   violently dying law kills the law, not the court).
2. `{{outRoot}}/conformance_court.exs` — the conformance court: compiles the
   rendered suite, defines a real Agent-backed reference store implementing the
   specimen contract, one sabotage wrapper per `scb:Mutant` row (every callback
   delegates to the reference store except the broken callback, which raises),
   then requires the suite to pass the reference store AND refuse every
   sabotaged store. Exit 1 on any violated invariant.

## Consumer integration steps

1. Copy the pack (or reference `--pack-dir`); replace the specimen
   `scb:Target` row (suiteModule/behaviorModule/referenceStoreModule/outRoot +
   bootBody/startBody) with YOUR modules and fixtures, the specimen
   `scb:Callback` rows with YOUR behaviour's callbacks, the specimen `scb:Law`
   rows with YOUR behavioural laws (executable Elixir bodies where `mod` is the
   store under test and `s` the started store), and add one `scb:Mutant` row
   per callback worth breaking.
2. Render:
   `MIX_BUILD_ROOT=_build-x5 mix ggen_igniter.sync --pack-dir <pack> --template <pack>/templates/store_conformance.ex.eex --engine oxigraph --on-stale prune --out <suite>.ex --manifest-dir <mf> --verify-cwd <project>`
   (and likewise for the court template).
3. Run the court: `elixir <outRoot>/conformance_court.exs` — exit 0 proves both
   directions (reference store passes; every mutant is refused, by laws that
   actually cover the broken callback).
4. Use the suite in YOUR test tree:
   `use <%= ... %>Suite, store: MyStore, start: &MyStore.start/0`-style via the
   `__using__` macro (store + start are consumer arguments, never embedded).

## What it intentionally does NOT do

- No ash_pplan embedding: rendered modules are consumer-namespaced; the
  specimen contract (lease-KV) is a specimen, not a dependency.
- No mock stores: the court runs a real Agent-backed reference store and real
  sabotage wrappers (Chicago-style), and requires the erroring laws to actually
  cover the broken callback (anti-vacuity by construction, not by assertion).
- No engine lock-in beyond ggen_igniter's oxigraph default; gates stay
  ORDER BY'd, no positional filter args, no literal `{%` anywhere in the pack
  (Tera-parse-safe), PREFIXes complete.
