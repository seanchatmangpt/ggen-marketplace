#!/usr/bin/env bash
# Court delegation-admission-pack -- migrated from .github/workflows/delegation-admission-pack.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute positive and negative gate witnesses
echo "::group::delegation-admission-pack: Execute positive and negative gate witnesses"
(
set -e
python packs/delegation-admission-pack/qualification/verify.py
)
echo "::endgroup::"
