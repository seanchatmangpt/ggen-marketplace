#!/usr/bin/env bash
# Court measure-r66-receipt-realization -- migrated from .github/workflows/measure-r66-receipt-realization.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute R66 permanent court
echo "::group::measure-r66-receipt-realization: Execute R66 permanent court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r66_receipt_realization_calibration.py
)
echo "::endgroup::"
# --- Verify generation contract owns R66 projection
echo "::group::measure-r66-receipt-realization: Verify generation contract owns R66 projection"
(
set -eo pipefail
set -euo pipefail
grep -F 'name = "receipt-realization-calibration"' packs/epistemic-sensor-factory-pack/ggen.toml
grep -F 'queries/1502_r66_receipt_realization_projection.rq' packs/epistemic-sensor-factory-pack/ggen.toml
grep -F 'templates/r66-receipt-realization-calibration.json.tera' packs/epistemic-sensor-factory-pack/ggen.toml
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r66-receipt-realization: Refuse ambient consequential actuation"
(
set -eo pipefail
set -euo pipefail
! grep -R --line-number -E 'consequential_do[" ]*:[ ]*true|odrl:execute' \
  packs/epistemic-sensor-factory-pack/fixtures/r66-receipt-realization-calibration.ttl \
  packs/epistemic-sensor-factory-pack/queries/*_r66_*.rq \
  packs/epistemic-sensor-factory-pack/templates/r66-receipt-realization-calibration.json.tera
)
echo "::endgroup::"
