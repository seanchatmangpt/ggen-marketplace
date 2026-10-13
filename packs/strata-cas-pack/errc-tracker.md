# errc-tracker.md — strata-cas-pack hardening wave 2026-10-13

ERRC pass; citations re-verified at write time.

## Eliminate

Legacy `templates/cas.rs.tmpl` deleted (superseded by
`templates/cas.rs.tera` + `ggen.toml` `cas-merkle` rule). `[dependencies]`
removed (FM-PACK-014).

## Reduce

Ontology/template disconnect reduced: the static struct body is now
emitted by a wired `.tera` under a real generation rule; the empty
projection carries the literal `// REFUSED: empty ontology projection`
marker (zero individuals is current ontology truth, fail-closed).

## Raise

`gates/010_snapshot_abutment.rq` and `gates/020_wormhole_digest_shape.rq`
landed. Honest disclosure: with zero individuals both pass vacuously —
they are non-vacuous only after real commit data lands.

## Create

`ggen.toml`, `queries/commits.rq` (OPTIONAL parent), `cas.rs.tera`,
`generated/cas.rs` (sha256 9f2dcda9…) — new this wave. Grounding intact:
`~/strata/strata_protocol/src/cas.rs:279` `CasSnapshotLedger` (push at
:293) — ontology comment resolves to real source.
