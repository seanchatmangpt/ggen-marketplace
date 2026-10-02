#!/usr/bin/env bash
# Court develop-selection-capital -- migrated from .github/workflows/develop-selection-capital.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Refuse ambient DO in pack source
echo "::group::develop-selection-capital: Refuse ambient DO in pack source"
(
set -e
! grep -R -E "(requests\.(post|put|patch|delete)|subprocess\.|os\.system)" packs/dfcm-pack/families/selection-capital
)
echo "::endgroup::"
