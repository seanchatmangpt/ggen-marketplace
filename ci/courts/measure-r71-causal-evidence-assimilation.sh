#!/usr/bin/env bash
# Court measure-r71-causal-evidence-assimilation -- migrated from .github/workflows/measure-r71-causal-evidence-assimilation.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute 50-sensor assimilation court
echo "::group::measure-r71-causal-evidence-assimilation: Execute 50-sensor assimilation court"
(
set -e
python3 packs/control-plane-causality-observability-pack/r71/tests/test_contract.py
)
echo "::endgroup::"
# --- Refuse ambient consequential DO
echo "::group::measure-r71-causal-evidence-assimilation: Refuse ambient consequential DO"
(
set -e
! grep -R -E 'cea:actuationPerformed[[:space:]]+true|cea:generatedOutputEdited[[:space:]]+true' packs/control-plane-causality-observability-pack/r71/fixtures
)
echo "::endgroup::"
