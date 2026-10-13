# errc-tracker.md — strata-stratus-pack hardening wave 2026-10-13

ERRC pass; citations re-verified at write time.

## Eliminate

Legacy `templates/stratus.rs.tmpl` deleted (superseded by split
`valves.rs.tera`/`registers.rs.tera`). `[dependencies]` removed
(FM-PACK-014).

## Reduce

Duplicate-struct hazard: the old single template emitted
`WitnessValve`/`StateRegister` definitions inside per-row loops; the two
-rule split defines each struct exactly once (grep-counted in
`generated/valves.rs` / `generated/registers.rs`).

## Raise

`gates/010_register_guards.rq`: exactly-one `st:guardedBy` →
`st:WitnessValve` per register; negative witness (missing guardedBy on
MainRegister) refused FM-LAW-018. Boolean rendering verified bare
`true` in output.

## Create

Two-rule `ggen.toml`, `queries/{valves,registers}.rq`, two `.tera`
templates, two generated outputs — new this wave; double-sync
byte-identical.
