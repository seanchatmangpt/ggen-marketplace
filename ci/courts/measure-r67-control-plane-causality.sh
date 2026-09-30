#!/usr/bin/env bash
# Court measure-r67-control-plane-causality -- migrated from .github/workflows/measure-r67-control-plane-causality.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Run 50-sensor court
echo "::group::measure-r67-control-plane-causality: Run 50-sensor court"
(
set -e
python3 packs/control-plane-causality-observability-pack/tests/test_contract.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r67-control-plane-causality: Refuse ambient consequential actuation"
(
set -e
! grep -R "actuationPerformed true" packs/control-plane-causality-observability-pack/fixtures
)
echo "::endgroup::"
