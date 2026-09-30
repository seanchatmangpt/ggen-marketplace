#!/usr/bin/env bash
# Court implement-r74-structural-replication -- migrated from .github/workflows/implement-r74-structural-replication.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute R73 producer court
echo "::group::implement-r74-structural-replication: Execute R73 producer court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/test_r73_structural_revops.py
)
echo "::endgroup::"
# --- Execute R74 structural replication court
echo "::group::implement-r74-structural-replication: Execute R74 structural replication court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/test_r74_structural_replication.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::implement-r74-structural-replication: Refuse ambient consequential actuation"
(
set -e
! grep -R -E 'actuationPerformed[[:space:]]+true|consequential_do[[:space:]]*=[[:space:]]*true' packs/epistemic-sensor-factory-pack/ontology.r73-structural-revops.ttl packs/epistemic-sensor-factory-pack/fixtures/r73-structural-revops.ttl
)
echo "::endgroup::"
