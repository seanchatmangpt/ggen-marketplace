#!/usr/bin/env bash
# Court measure-r65-epistemic-reinvestment -- migrated from .github/workflows/measure-r65-epistemic-reinvestment.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute R65 50-sensor court
echo "::group::measure-r65-epistemic-reinvestment: Execute R65 50-sensor court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r65_epistemic_reinvestment.py
)
echo "::endgroup::"
# --- Refuse ambient consequential DO
echo "::group::measure-r65-epistemic-reinvestment: Refuse ambient consequential DO"
(
set -e
! grep -R 'actuationPerformed true' packs/epistemic-sensor-factory-pack/fixtures/r65-epistemic-reinvestment.ttl
! grep -R 'odrl:permission.*execute' packs/epistemic-sensor-factory-pack/ontology.r65-epistemic-reinvestment.ttl
)
echo "::endgroup::"
