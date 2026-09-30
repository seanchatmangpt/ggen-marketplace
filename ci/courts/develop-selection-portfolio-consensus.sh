#!/usr/bin/env bash
# Court develop-selection-portfolio-consensus -- migrated from .github/workflows/develop-selection-portfolio-consensus.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile pack
echo "::group::develop-selection-portfolio-consensus: Compile pack"
(
set -e
python3 -m compileall -q packs/dfcm-selection-portfolio-consensus-pack
)
echo "::endgroup::"
# --- Run permanent court
echo "::group::develop-selection-portfolio-consensus: Run permanent court"
(
set -e
python3 -m unittest -v packs/dfcm-selection-portfolio-consensus-pack/tests/test_portfolio_consensus.py
)
echo "::endgroup::"
# --- Refuse ambient consequential DO
echo "::group::develop-selection-portfolio-consensus: Refuse ambient consequential DO"
(
set -e
! grep -R -nE "requests\.(post|put|patch|delete)|subprocess\.|os\.system" packs/dfcm-selection-portfolio-consensus-pack/scripts
)
echo "::endgroup::"
