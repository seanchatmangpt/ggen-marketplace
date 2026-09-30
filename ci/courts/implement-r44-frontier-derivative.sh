#!/usr/bin/env bash
# Court implement-r44-frontier-derivative -- migrated from .github/workflows/implement-r44-frontier-derivative.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Qualify frontier derivative contract
echo "::group::implement-r44-frontier-derivative: Qualify frontier derivative contract"
(
set -e
python3 packs/frontier-derivative-pack/tests/test_contract.py
)
echo "::endgroup::"
# --- Execute all fifty frontier derivative courts
echo "::group::implement-r44-frontier-derivative: Execute all fifty frontier derivative courts"
(
set -e
python3 packs/frontier-derivative-pack/scripts/execute_qualification_queries.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::implement-r44-frontier-derivative: Refuse ambient consequential actuation"
(
set -e
! grep -R 'fd:authority "DO"\|actuation_performed": *true' \
  packs/frontier-derivative-pack/ontology.ttl \
  packs/frontier-derivative-pack/templates \
  packs/frontier-derivative-pack/fixtures
)
echo "::endgroup::"
