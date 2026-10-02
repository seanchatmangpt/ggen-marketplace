# ash-pplan-protocol-court-pack

Generalizes ash_pplan's TLA+/Stateright differential protocol-court machinery —
machinery that exists in no other marketplace pack — into reusable,
consumer-facing manufacturing capital.

## What it manufactures

Rendered per consumer protocol (a `pcp:Protocol` row + `pcp:State`,
`pcp:Transition`, `pcp:Action`, `pcp:Guard`, `pcp:Property` rows; every formerly
template-hardcoded value — module name, machine label, worker/step sets, init
block, variables, WF action, cfg constants, the parked/forward state classes —
is an ontology fact, and no ash_pplan module is ever embedded):

1. `<moduleName>.tla` — the TLA+ module: statuses/terminal/parked/forward sets,
   Init, every action with its guards as `\* guard:` annotations, Next, every
   property, and the WF fairness clause.
2. `<moduleName>.cfg` — the TLC config: SPECIFICATION, CONSTANTS, INVARIANT and
   PROPERTY lines derived from each property row's `pcp:kind`.
3. `stateright/model.rs` — the Stateright differential model skeleton: the same
   vocabulary (STATUSES/TERMINAL/PARKED/FORWARD/ACTIONS/GUARDS/PROPERTIES) as
   the TLA+, plus `MUTANT_GUARD_DROPS` from the `pcp:Mutant` rows, and an
   embedded vocabulary test (`cargo test`) asserting the vocabulary is closed
   (every parked/forward/terminal state is a declared status; every declared
   mutant drops a guard that actually exists).
4. `<module>_transitions.exs` — the Elixir transition table (statuses, terminal
   set, transition pairs) the differential trace court consumes.

## Consumer integration steps

1. Copy the pack (or reference `--pack-dir`); replace the specimen
   `pcp:Protocol`/`pcp:State`/`pcp:Transition`/`pcp:Action`/`pcp:Guard`/
   `pcp:Property`/`pcp:Mutant` rows with YOUR protocol.
2. Render (per template):
   `MIX_BUILD_ROOT=_build-x5 mix ggen_igniter.sync --pack-dir <pack> --template <pack>/templates/protocol.tla.eex --engine oxigraph --on-stale prune --out <module>.tla --manifest-dir <mf> --verify-cwd <project>`
3. Model-check: TLC on the .tla/.cfg; Stateright on model.rs (`cargo test` for
   the vocabulary court, then your full state-space check). A verdict
   disagreement between checkers is a court failure, not a modeling drift.
4. Mutants: each `pcp:Mutant` row drops one guard id; your differential court
   REQUIRES a counterexample for every declared mutant (a mutant with no
   counterexample is an admission failure, not an expected outcome). The
   rendered `MUTANT_GUARD_DROPS` + embedded vocabulary test enforce closure of
   the mutant set against the declared guards.

## What it intentionally does NOT do

- No ash_pplan embedding: the specimen protocol (claim/lease, park, signal,
  cancel/unwind) is a specimen, not a dependency; rendered artifacts name only
  the consumer's ontology rows.
- No checker runtime in the pack: TLC/Stateright execution stays in the
  consumer's court; the pack manufactures the checked artifacts from ONE
  ontology.
- Gates stay ORDER BY'd, no positional filter args, no literal `{%` anywhere in
  the pack (Tera-parse-safe), PREFIXes complete.
