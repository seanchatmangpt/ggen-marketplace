#!/usr/bin/env bash
# Court measure-r45b-replication-yield -- migrated from .github/workflows/measure-r45b-replication-yield.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Preserve cumulative sensor contract
echo "::group::measure-r45b-replication-yield: Preserve cumulative sensor contract"
(
set -e
python3 packs/replication-epistemic-observability-pack/tests/test_contract.py
)
echo "::endgroup::"
# --- Execute R43 immutable baseline
echo "::group::measure-r45b-replication-yield: Execute R43 immutable baseline"
(
set -e
python3 packs/replication-epistemic-observability-pack/scripts/execute_reference.py
)
echo "::endgroup::"
# --- Execute R45B replication-yield tranche
echo "::group::measure-r45b-replication-yield: Execute R45B replication-yield tranche"
(
set -e
python3 packs/replication-epistemic-observability-pack/scripts/execute_r45b.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r45b-replication-yield: Refuse ambient consequential actuation"
(
set -e
! grep -R 'actuation_performed":true\|actuationPerformed true' packs/replication-epistemic-observability-pack/fixtures packs/replication-epistemic-observability-pack/templates
)
echo "::endgroup::"
