#!/usr/bin/env bash
# Court measure-r73-structural-revops -- migrated from .github/workflows/measure-r73-structural-revops.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute R73 structural RevOps court
echo "::group::measure-r73-structural-revops: Execute R73 structural RevOps court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/test_r73_structural_revops.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r73-structural-revops: Refuse ambient consequential actuation"
(
set -e
! grep -R -E 'actuationPerformed[[:space:]]+true|consequential_do[[:space:]]*=[[:space:]]*true' packs/epistemic-sensor-factory-pack/ontology.r73-structural-revops.ttl packs/epistemic-sensor-factory-pack/fixtures/r73-structural-revops.ttl
)
echo "::endgroup::"
