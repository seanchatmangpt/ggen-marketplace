#!/usr/bin/env bash
# Court develop-r63-relief-capital-allocation -- migrated from .github/workflows/develop-r63-relief-capital-allocation.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute R63 permanent court
echo "::group::develop-r63-relief-capital-allocation: Execute R63 permanent court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r63_relief_capital_allocation.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::develop-r63-relief-capital-allocation: Refuse ambient consequential actuation"
(
set -eo pipefail
grep -q '"consequential_do":false' receipts/develop/2026-08-25-r63-relief-capital-allocation.json
! grep -R -E '(^|[^A-Z])(INSERT|DELETE|LOAD|CLEAR|DROP|CREATE|MOVE|COPY|ADD|SERVICE)[[:space:]]' packs/epistemic-sensor-factory-pack/queries/13*_r63_*.rq
)
echo "::endgroup::"
