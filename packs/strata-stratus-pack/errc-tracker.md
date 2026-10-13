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
byte-identical. S21 repair: `templates/registers.rs.tera` now emits
`use super::valves::WitnessValve;` (sibling-module import, one-line
family comment). Witness receipt: `ggen sync run` x2 byte-identical
(sha256 `3144bb4d7d224ce9bb8369cb30cfe54a77129ca743b97f20166606a15f33f6bc`);
joint-crate rustc --edition 2021 compile of generated
`valves.rs`+`registers.rs` as sibling modules passes and the admit()
witness binary prints `ADMIT_OK register=main values=["t0"]`
(valve `VALVE_DEFAULT`, register const `MAIN_NAME`). S16 audit defect
(standalone rustc `cannot find type WitnessValve`) closed.
