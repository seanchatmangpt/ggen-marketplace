#!/usr/bin/env bash
# Court implement-r75-structural-realization -- migrated from .github/workflows/implement-r75-structural-realization.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute R74 structural replication court
echo "::group::implement-r75-structural-realization: Execute R74 structural replication court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/test_r74_structural_replication.py
)
echo "::endgroup::"
# --- Execute R75 structural realization court
echo "::group::implement-r75-structural-realization: Execute R75 structural realization court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/test_r75_structural_realization.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::implement-r75-structural-realization: Refuse ambient consequential actuation"
(
set -e
! grep -R -E 'consequentialDo[[:space:]]+true|actuationPerformed[[:space:]]+true|consequential_do[[:space:]]*=[[:space:]]*true' packs/epistemic-sensor-factory-pack/ontology.r75-structural-realization.ttl packs/epistemic-sensor-factory-pack/fixtures/r75-structural-realization.ttl
)
echo "::endgroup::"
