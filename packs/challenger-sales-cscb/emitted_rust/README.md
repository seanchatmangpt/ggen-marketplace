# emitted_rust/

ggen-synced emission of the pack's Rust runner crate, produced by the three
`rust-runner-*` `[[generation.rules]]` entries in this pack's `ggen.toml`
(manifest, cycle counter, main). The crate here is tracked source of truth
for the pack; regenerate it with `ggen sync run` against the pack manifest,
never hand-edit the generated files.

`results/` holds benchmark run output from executing the runner. It is
gitignored regenerable run output (see the `.gitignore` rule added
2026-11-07), not evidence — re-run the runner to reproduce it.
