#!/usr/bin/env bash
# Court portfolio-r70-autocatalytic-capital-yield -- migrated from .github/workflows/portfolio-r70-autocatalytic-capital-yield.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute R70 causal capital-yield courts
echo "::group::portfolio-r70-autocatalytic-capital-yield: Execute R70 causal capital-yield courts"
(
set -e
python3 packs/epistemic-sensor-factory-pack/r70/tests/test_contract.py
)
echo "::endgroup::"
# --- Refuse ambient consequential DO
echo "::group::portfolio-r70-autocatalytic-capital-yield: Refuse ambient consequential DO"
(
set -e
set -euo pipefail
! grep -R -E 'acy:actuationPerformed[[:space:]]+true' packs/epistemic-sensor-factory-pack/r70
grep -q 'acy:handEditedGeneratedCount 0' packs/epistemic-sensor-factory-pack/r70/fixtures/reference.ttl
grep -q 'acy:authorityViolationCount 0' packs/epistemic-sensor-factory-pack/r70/fixtures/reference.ttl
)
echo "::endgroup::"
