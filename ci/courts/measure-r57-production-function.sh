#!/usr/bin/env bash
# Court measure-r57-production-function -- migrated from .github/workflows/measure-r57-production-function.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute R57 production-function court
echo "::group::measure-r57-production-function: Execute R57 production-function court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r57_production_function.py
)
echo "::endgroup::"
# --- Execute R58 independent-consumer-factor court
echo "::group::measure-r57-production-function: Execute R58 independent-consumer-factor court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r58_consumer_factor.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r57-production-function: Refuse ambient consequential actuation"
(
set -eo pipefail
set -euo pipefail
if grep -R -nE 'actuationPerformed[[:space:]]+true|CONSEQUENTIAL_DO=true' packs/epistemic-sensor-factory-pack/fixtures/r57-production-function.ttl packs/epistemic-sensor-factory-pack/fixtures/r58-consumer-factor.ttl receipts/measure/2026-08-25-r57-production-function.json 2>/dev/null; then
  echo 'REFUSED[AMBIENT_CONSEQUENTIAL_DO]'
  exit 1
fi
echo 'R58_CONSEQUENTIAL_DO=false'
)
echo "::endgroup::"
