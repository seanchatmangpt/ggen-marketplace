#!/usr/bin/env bash
# Court measure-sequential-policy-calibration -- migrated from .github/workflows/measure-sequential-policy-calibration.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Verify calibration court surface
echo "::group::measure-sequential-policy-calibration: Verify calibration court surface"
(
set -e
test "$(find packs/dfcm-maximalist-court-pack/queries -maxdepth 1 -name 'cal-*.rq' | wc -l)" -ge 30
grep -q 'PolicyCalibrationObservation' packs/dfcm-maximalist-court-pack/ontology.ttl
grep -q 'predictedStopProbability' packs/dfcm-maximalist-court-pack/ontology.ttl
grep -q 'decisionLoss' packs/dfcm-maximalist-court-pack/ontology.ttl
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-sequential-policy-calibration: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'curl |wget |requests\.(post|put|patch|delete)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/dfcm-maximalist-court-pack/queries/cal-*.rq
)
echo "::endgroup::"
