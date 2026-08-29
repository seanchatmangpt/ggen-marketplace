# generated/ — real, deployed OCEL accumulator service

This directory deviates from the pack's usual source-only convention
(ontology.ttl/templates/gates committed, `generated/` left untracked and
regenerable) for one reason: `src/bin/ocel_accumulator.rs` is a real,
hand-authored, currently-deployed service (istio-system's
`ocel-accumulator` Deployment on the kind-platform-eng-colima cluster),
not output reproducible by `ggen sync run` alone.

- `src/otel_to_ocel.rs`, `src/lib.rs`, `tests/real_trace_transform.rs` —
  ARE reproducible via `ggen sync run` against `../ontology.ttl` and
  `../templates/`. Committed here anyway so `docker build` has a complete,
  self-contained build context without a `ggen` binary being available at
  image-build time (confirmed byte-identical to a fresh regen as of this
  commit -- see the pack's git history).
- `src/bin/ocel_accumulator.rs`, `Cargo.toml`, `Cargo.lock`,
  `Dockerfile.ocel-accumulator` — hand-written, not ggen-templated. This
  is real application code, committed because it's the actual source for
  a real running service, the same reason any other deployed binary's
  source lives in version control.

If you regenerate `otel_to_ocel.rs`/`lib.rs` via ggen, re-verify they
still match this file's committed content (or re-run `cargo +nightly
test`) before rebuilding the Docker image.
