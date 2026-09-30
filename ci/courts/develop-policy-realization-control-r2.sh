#!/usr/bin/env bash
# Court develop-policy-realization-control-r2 -- migrated from .github/workflows/develop-policy-realization-control-r2.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile reusable control
echo "::group::develop-policy-realization-control-r2: Compile reusable control"
(
set -e
python3 -m py_compile packs/evidence-capital-policy-adaptive-control-pack/scripts/*.py packs/evidence-capital-policy-adaptive-control-pack/tests/*.py
)
echo "::endgroup::"
# --- Permanent adaptive-control court
echo "::group::develop-policy-realization-control-r2: Permanent adaptive-control court"
(
set -e
export PYTHONPATH="packs/evidence-capital-policy-adaptive-control-pack"
python3 -m unittest discover -s packs/evidence-capital-policy-adaptive-control-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Refuse ambient consequential DO
echo "::group::develop-policy-realization-control-r2: Refuse ambient consequential DO"
(
set -e
! grep -R -E "(subprocess\.|os\.system|requests\.(post|put|patch|delete))" packs/evidence-capital-policy-adaptive-control-pack/scripts packs/evidence-capital-policy-adaptive-control-pack/tests
)
echo "::endgroup::"
