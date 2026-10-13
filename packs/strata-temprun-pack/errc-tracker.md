# errc-tracker.md — strata-temprun-pack hardening wave 2026-10-13

ERRC pass over the 2026-10-13 hardening wave. Every entry cites a real
source at `file:line`, re-verified at write time — no paraphrase
substituted for a citation.

## Eliminate

Done in-wave: legacy v1 template `templates/arena.rs.tmpl` deleted
(superseded by `templates/arena.rs.tera`, wired by `ggen.toml`
`temprun-arenas` rule). `pack.toml` `[dependencies]` removed
(FM-PACK-014; commit 513a1a64c).

## Reduce

Namespace debt: ontology is already on the family kernel namespace
`https://strata.chatman.ai/ontology#`; no split remains in this pack.

## Raise

`st:admissionFuel 3` now a valued individual fact (was unvalued
property), grounded to `~/strata/temprun/src/lib.rs:60` `run/2` with
exactly three `fuel.charge(1)` steps. Projected as
`ARENA_DEFAULT_MAX_FUEL` in `generated/arena.rs` and gated by
`gates/010_fuel_positive.rq` (negative witness: admissionFuel 2 →
FM-LAW-018 refusal). Repair lane S5 (audit R15): `st:admissionFuel` now
also projected as `ARENA_DEFAULT_ADMISSION_FUEL_MIN: u64 = 3` per arena
row — `queries/arenas.rq` extends SELECT with REQUIRED `?admission_fuel`
bound to `st:admissionFuel` (fail-closed, signer `keys.rq` pattern);
`templates/arena.rs.tera` emits the constant; banner now carries the
namespace. Verified: `ggen sync run` ×2 byte-identical (pass 2
"skipped: unchanged: content identical", graph_hash_hex
af041512fb63aa1eaf8076f6c3bf8efd38024fdd8f868b3c9767957b46a69abd);
`rustc --edition 2021 --crate-type lib generated/arena.rs` exit 0.

## Create

`ggen.toml`, `queries/arenas.rq`, `templates/arena.rs.tera`,
`generated/arena.rs`, `gates/010_fuel_positive.rq` — all new this wave;
double-sync byte-identical (sha256 aa50844a… at write time; superseded by f00d5e13… after the admissionFuel projection + banner regen).
