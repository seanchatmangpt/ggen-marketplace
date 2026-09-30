#!/usr/bin/env bash
# Court measure-evidence-capital-policy-realization -- migrated from .github/workflows/measure-evidence-capital-policy-realization.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile policy-realization pack
echo "::group::measure-evidence-capital-policy-realization: Compile policy-realization pack"
(
set -e
python3 -m py_compile packs/evidence-capital-policy-realization-pack/scripts/*.py packs/evidence-capital-policy-realization-pack/tests/*.py
)
echo "::endgroup::"
# --- Run permanent policy-realization courts
echo "::group::measure-evidence-capital-policy-realization: Run permanent policy-realization courts"
(
set -e
export PYTHONPATH="packs/evidence-capital-policy-realization-pack"
python3 -m unittest discover -s packs/evidence-capital-policy-realization-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-evidence-capital-policy-realization: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/evidence-capital-policy-realization-pack/scripts packs/evidence-capital-policy-realization-pack/tests
)
echo "::endgroup::"
