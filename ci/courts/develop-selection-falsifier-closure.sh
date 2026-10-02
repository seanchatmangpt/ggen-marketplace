#!/usr/bin/env bash
# Court develop-selection-falsifier-closure -- migrated from .github/workflows/develop-selection-falsifier-closure.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile reusable control
echo "::group::develop-selection-falsifier-closure: Compile reusable control"
(
set -e
python3 -m py_compile packs/dfcm-pack/families/selection-falsifier-closure/scripts/*.py packs/dfcm-pack/families/selection-falsifier-closure/tests/*.py
)
echo "::endgroup::"
# --- Permanent control court
echo "::group::develop-selection-falsifier-closure: Permanent control court"
(
set -e
export PYTHONPATH="packs/dfcm-pack/families/selection-falsifier-closure"
python3 -m unittest discover -s packs/dfcm-pack/families/selection-falsifier-closure/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Refuse ambient consequential DO
echo "::group::develop-selection-falsifier-closure: Refuse ambient consequential DO"
(
set -e
! grep -R -E "(subprocess\.|os\.system|requests\.(post|put|patch|delete))" packs/dfcm-pack/families/selection-falsifier-closure/scripts packs/dfcm-pack/families/selection-falsifier-closure/tests
)
echo "::endgroup::"
