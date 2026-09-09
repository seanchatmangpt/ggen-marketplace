#!/usr/bin/env bash
set -euo pipefail
# Canonicalize, don't just check: rustfmt's line-wrap decisions are
# content-length-dependent, so a static Tera template cannot emit text
# guaranteed rustfmt --check-clean for arbitrary future ontology strings.
# Formatting is therefore this ladder's job, not the template's; clippy and
# test remain real, non-mutating gates.
cargo fmt --all
cargo clippy --all-targets -- -D warnings
cargo test --all-targets
