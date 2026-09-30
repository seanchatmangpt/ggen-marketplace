#!/usr/bin/env bash
# Court measure-r76-portfolio-structural-census -- migrated from .github/workflows/measure-r76-portfolio-structural-census.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute R76 court
echo "::group::measure-r76-portfolio-structural-census: Execute R76 court"
(
set -e
pytest -q packs/portfolio-epistemic-observability-pack/tests/test_r76_structural_census.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r76-portfolio-structural-census: Refuse ambient consequential actuation"
(
set -e
if grep -R -nE 'actuationPerformed[[:space:]]+true|consequential_do[[:space:]]*[:=][[:space:]]*true' packs/portfolio-epistemic-observability-pack/ontology.r76-structural-census.ttl packs/portfolio-epistemic-observability-pack/fixtures/r76-structural-census.ttl; then exit 1; fi
)
echo "::endgroup::"
