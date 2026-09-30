#!/usr/bin/env bash
# Court measure-r43-replication-epistemic -- migrated from .github/workflows/measure-r43-replication-epistemic.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Qualify immutable sensor contract
echo "::group::measure-r43-replication-epistemic: Qualify immutable sensor contract"
(
set -e
python3 packs/replication-epistemic-observability-pack/tests/test_contract.py
)
echo "::endgroup::"
# --- Execute all fifty sensors on grounded fixture
echo "::group::measure-r43-replication-epistemic: Execute all fifty sensors on grounded fixture"
(
set -e
python3 packs/replication-epistemic-observability-pack/scripts/execute_reference.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r43-replication-epistemic: Refuse ambient consequential actuation"
(
set -e
! grep -R 'actuation_performed":true\|actuationPerformed true' \
  packs/replication-epistemic-observability-pack/fixtures \
  packs/replication-epistemic-observability-pack/templates \
  receipts/measure/2026-08-25-r43-replication-epistemic-observability.json
)
echo "::endgroup::"
