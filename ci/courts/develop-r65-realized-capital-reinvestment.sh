#!/usr/bin/env bash
# Court develop-r65-realized-capital-reinvestment -- migrated from .github/workflows/develop-r65-realized-capital-reinvestment.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute R65 permanent court
echo "::group::develop-r65-realized-capital-reinvestment: Execute R65 permanent court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r65_realized_capital_reinvestment.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::develop-r65-realized-capital-reinvestment: Refuse ambient consequential actuation"
(
set -eo pipefail
grep -q '"consequential_do":false' receipts/develop/2026-08-25-r65-realized-capital-reinvestment.json
! grep -R -E '(^|[^A-Z])(INSERT|DELETE|LOAD|CLEAR|DROP|CREATE|MOVE|COPY|ADD|SERVICE)[[:space:]]' packs/epistemic-sensor-factory-pack/queries/14*_r65_*.rq
)
echo "::endgroup::"
