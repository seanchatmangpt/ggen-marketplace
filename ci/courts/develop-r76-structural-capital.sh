#!/usr/bin/env bash
# Court develop-r76-structural-capital -- migrated from .github/workflows/develop-r76-structural-capital.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute R76 structural-capital court
echo "::group::develop-r76-structural-capital: Execute R76 structural-capital court"
(
set -e
pytest -q packs/epistemic-sensor-factory-pack/tests/test_r76_structural_capital.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::develop-r76-structural-capital: Refuse ambient consequential actuation"
(
set -e
if grep -R -nE 'actuationPerformed[[:space:]]+true|consequential_do[[:space:]]*[:=][[:space:]]*true' packs/epistemic-sensor-factory-pack/ontology.r76-structural-capital-compiler.ttl packs/epistemic-sensor-factory-pack/fixtures/r76-structural-capital.ttl; then exit 1; fi
)
echo "::endgroup::"
