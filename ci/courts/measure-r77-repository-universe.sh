#!/usr/bin/env bash
# Court measure-r77-repository-universe -- migrated from .github/workflows/measure-r77-repository-universe.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Run R77 exact-universe court
echo "::group::measure-r77-repository-universe: Run R77 exact-universe court"
(
set -e
python -m pytest -q packs/portfolio-epistemic-observability-pack/tests/test_r77_repository_universe.py
)
echo "::endgroup::"
# --- Compile collector
echo "::group::measure-r77-repository-universe: Compile collector"
(
set -e
python -m py_compile packs/portfolio-epistemic-observability-pack/scripts/r77_repository_universe.py
)
echo "::endgroup::"
# --- Refuse consequential actuation
echo "::group::measure-r77-repository-universe: Refuse consequential actuation"
(
set -e
! grep -R -E 'consequential_do[[:space:]]*[:=][[:space:]]*true|actuationPerformed[[:space:]]+true' packs/portfolio-epistemic-observability-pack/ontology.r77-repository-universe.ttl packs/portfolio-epistemic-observability-pack/fixtures/r77-repository-universe.ttl
)
echo "::endgroup::"
