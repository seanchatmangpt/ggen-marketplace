#!/usr/bin/env bash
# Court challenger-value-court -- migrated from .github/workflows/challenger-value-court.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute Challenger conformance vectors
echo "::group::challenger-value-court: Execute Challenger conformance vectors"
(
set -e
python packs/challenger-value-framing-pack/reference/python/court.py
)
echo "::endgroup::"
