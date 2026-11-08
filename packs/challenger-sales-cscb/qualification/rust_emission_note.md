# Qualification Note — CSCB Rust Emission (lane R7)

Standing: PARTIAL_ALIVE
Date: 2026-11-07
Repo: /Users/sac/ggen-marketplace (no git commands run — per lane contract)

## What landed

- `templates/rust/Cargo.toml.tmpl` — manifest: zero third-party deps in the
  default profile, `criterion` optional behind `bench` feature, release
  profile with lto/codegen-units=1/panic=abort.
- `templates/rust/cycle_counter.rs.tmpl` — cfg-gated cycle reads: RDTSCP via
  `core::arch::x86_64` on x86_64, CNTVCT_EL0 inline asm on aarch64, and a
  fail-closed `compile_error!` on any other target (no silent fake counter).
  Includes a monotonic-within-window unit test.
- `templates/rust/main.rs.tmpl` — core-pinned worker loop skeleton
  (pin-to-core-0 on Linux, honest unpinned WARN elsewhere), insertion-sort +
  nearest-rank percentiles, self-contained CSV + JSON emission, CRC32 (IEEE,
  poly 0xEDB88320) over the CSV bytes, CRC mirrored into the JSON.
- `templates/rust/BINDING_CONTRACT.md` — variable table + sync addendum for
  R1/R14 (three `[[generation.rules]]` entries, output under `emitted_rust/`).
- `emitted_rust/README.md` — empty-until-sync placeholder.

## Emission state

NOT EMITTED via ggen: R1's `ggen.toml` does not yet include the
`templates/rust/` rule paths, so per the coordinate clause this lane placed
templates + sync addendum instead of running `ggen sync`. `emitted_rust/`
holds a README placeholder only.

## Compile smoke (real commands, real exits)

Hand-instantiated render (defaults per BINDING_CONTRACT.md: crate
`cscb-runner`, edition 2021, 6 stages S1..S6, 1000 warmup + 10000 iterations,
basename `cscb_results`) into a /tmp scratch crate. Three earlier attempts
failed during the RENDER step (my render script bugs: strip-regex mismatch on
the `{#- ... -}` Tera comment closer, and a dropped stages list) — these were
render-harness bugs, fixed before the passing run; the templates changed
twice for real defects found by the smoke:

1. Tera comment closer in Cargo.toml.tmpl was `-}` (invalid Tera), fixed to
   `-#}`.
2. `{{{{ output_basename }}}}` idiom produced literal `{{ }}` in Rust source;
   replaced with plain `{{ output_basename }}` (renders to the bare filename).
3. The JSON `write!` format string contained Rust-escaped braces
   (`{{\"stage\":...`) that real Tera would parse as template expressions;
   wrapped in `{% raw %}...{% endraw %}`.

Passing run (2026-11-07, Apple Silicon, cargo 1.97.0):

    TMPDIR=/tmp/cscb-runner-smoke.2O79 ... render: RENDER OK
    cargo test            # exit 0 — 1 passed, 0 failed (counter monotonic test)
    cargo run --release -- "$T/results"   # exit 0

Second full run with the unused-import fix (TMPDIR=/tmp/cscb-runner-smoke.Bk2W):

    cargo test            # exit 0, 1 passed, 0 failed, no warnings
    cargo run --release   # exit 0
    WARN: core pinning unavailable on this platform; results are unpinned

Final post-raw-block-fix re-run (TMPDIR=/tmp/cscb-runner-smoke.tBKB):
render exit 0, `cargo test` exit 0 — 1 passed, 0 failed.

Emitted results verified: cscb_results.csv (header + 6 stage rows, columns
stage/iterations/p50/p90/p99/min/max/mean_cycles) and cscb_results.json
(stage array + crc32_of_csv: 6558239), CRC32 over the CSV bytes present in
the JSON.

## Known measurement limitation (honest, not hidden)

On Apple Silicon (aarch64), CNTVCT_EL0 ticks at ~24-33 MHz; the skeleton's
per-iteration loop body completes in fewer ticks, so p50 reads 0 (observed:
p50=0, p99=41 on the smoke run — the counter resolves the loop body only
when it straddles a tick boundary). This is a counter-resolution limit, not
a template defect: the harness correctly reports what CNTVCT_EL0 can see.
Remediation path (NOT implemented in this lane): batch K iterations per
cycle-window sample on aarch64 so each sample straddles tick boundaries, or
divide by the arch-provided frequency register (CNTFRQ_EL0) to convert to
ns. Both are runner-behavior changes, so they belong to the runner's owner
lane / a follow-up order, with the BEAM harness (R5) unaffected (BEAM side
uses :erlang.monotonic_time, no such resolution limit).

## Scope honesty

`cscb-runner` measures Rust subjects on no_std/edge targets per
RFC-2026-0042 §4.1. BEAM-subject comparison lives in the BEAM harness
(lane R5). This harness is not a BEAM comparator;
any Rust-vs-BEAM claim must cite both harnesses (same host, same core
policy, same stage structure).
