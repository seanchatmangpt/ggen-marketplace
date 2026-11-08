# cargo-cicd-pack

Typed Rust projections for the [cargo-cicd](https://crates.io/crates/cargo-cicd)
command surface, manufactured from a source-audited RDF catalog. Version 0.2.0.

## What it projects

Six templates, all driven by the same filtered SPARQL over the pack's own
audited `cc:`/`cnv:` command individuals in `ontology.ttl` (52 rows: 51 live
commands across 21 nouns + 1 deprecated `cc:doctor-bare`):

| Template | Output | Freeze policy |
|---|---|---|
| `cargo_cicd_catalog.rs.tmpl` | `src/cargo_cicd_catalog.rs` | checksum |
| `cargo_cicd_proof.rs.tmpl` | `tests/cargo_cicd_catalog_proof.rs` (15 tests) | checksum |
| `cargo_cicd_dispatch.rs.tmpl` | `src/cargo_cicd_dispatch.rs` (51 wrapper fns) | checksum |
| `cargo_cicd_dispatch_proof.rs.tmpl` | `tests/cargo_cicd_dispatch_proof.rs` (9 tests) | checksum |
| `cargo_cicd_mod_wiring.rs.tmpl` | `src/cargo_cicd_lib_wiring.rs` | force |
| `cargo_cicd_reference.md.tmpl` | `docs/cargo_cicd_reference.md` | checksum |

- **Catalog**: typed constants (`CARGO_CICD_COMMANDS`, return-type/error-enum
  constants, `parse_args`, `args_are_consistent`) plus consistency proofs.
- **Dispatch**: one real `std::process::Command` wrapper per live command,
  shelling out to the installed `cargo-cicd` binary (a generic dispatcher, not
  a reimplementation of command behavior).
- **Reference doc**: per-command table with source-file citations.

All checksum-frozen outputs refuse silent clobber: a hand-edit makes the next
`ggen sync run` report `skipped: frozen`; picking up an ontology change
requires deleting the stale target file first (`FM-WRITE-005`, fail-closed).

## Consumer contract

`runtime = ["rust-std", "cargo"]` — generated code imports **only `std`**
(one `use std::process::Command`; every other `use` is intra-generated:
`cargo_cicd_catalog` / `cargo_cicd_dispatch`). No third-party crates are
required or emitted.

Peer context the consumer supplies:

- A crate of its own: `src/lib.rs` must `include!("cargo_cicd_lib_wiring.rs");`
  (the wiring template targets a pack-unique file, not `src/lib.rs`, to avoid
  `FM-WRITE-008` duplicate-output collisions when multiple inject-mode packs
  share one consumer).
- Command facts are shipped as this pack's own audited individuals; consumers
  may add their own `cnv:Command` rows under the `cc:` namespace and every
  template picks them up via the same filtered queries.
- Requires the `clap-noun-verb-pack` `cnv:` vocabulary (declared in
  `[capabilities].requires`).
- Optional peer: a `cargo-cicd` binary on PATH un-skips the 2 dispatch
  spawn-error tests; without it they self-skip (guarded, never fake-passed).

Compose the pack from a consumer `ggen.toml`:

```toml
[packs]
"cargo-cicd-pack" = { path = "<path-to-marketplace>/packs/cargo-cicd-pack" }
```

## Known disclosed gap

cargo-cicd's `lsp` noun (added upstream after the 2026-07-21 audit) is not yet
in the catalog — the "52 commands across 21 nouns" coverage claim is no longer
complete against the current target repo. Round-6 disclosure, unchanged here.

## Court

Scratch-consumer court (this wave, v0.2.0): real `ggen sync run` into a
disposable consumer crate at `/tmp`, real `cargo test` over the projected
catalog + dispatch proofs, structural validity of every rendered file, and an
anti-vacuity flip (ontology verb renamed → generated function renames with it,
then restored byte-exact). Commands and exits are recorded in
`docs/jira/v26.11.5/receipts/G16.md`.
