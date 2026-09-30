#!/usr/bin/env bash
# Court develop-remediation-counterfactual-safety -- migrated from .github/workflows/develop-remediation-counterfactual-safety.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile pack
echo "::group::develop-remediation-counterfactual-safety: Compile pack"
(
set -e
python3 -m compileall -q packs/owning-rail-remediation-counterfactual-pack
)
echo "::endgroup::"
# --- Run permanent court
echo "::group::develop-remediation-counterfactual-safety: Run permanent court"
(
set -e
python3 -m unittest -v packs/owning-rail-remediation-counterfactual-pack/tests/test_counterfactual_safety.py
)
echo "::endgroup::"
# --- Refuse ambient consequential DO
echo "::group::develop-remediation-counterfactual-safety: Refuse ambient consequential DO"
(
set -e
! grep -R -nE "requests\.(post|put|patch|delete)|subprocess\.|os\.system" packs/owning-rail-remediation-counterfactual-pack/scripts
)
echo "::endgroup::"
