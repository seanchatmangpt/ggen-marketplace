#!/usr/bin/env bash
# Court measure-r64-realized-capital-feedback -- migrated from .github/workflows/measure-r64-realized-capital-feedback.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute R64 permanent court
echo "::group::measure-r64-realized-capital-feedback: Execute R64 permanent court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r64_realized_capital_feedback.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r64-realized-capital-feedback: Refuse ambient consequential actuation"
(
set -eo pipefail
grep -q '"consequential_do":false' receipts/measure/2026-08-25-r64-realized-capital-feedback.json
! grep -R -E '(^|[^A-Z])(INSERT|DELETE|LOAD|CLEAR|DROP|CREATE|MOVE|COPY|ADD|SERVICE)[[:space:]]' packs/epistemic-sensor-factory-pack/queries/13*_r64_*.rq packs/epistemic-sensor-factory-pack/queries/1400_r64_*.rq
)
echo "::endgroup::"
