#!/usr/bin/env bash
# Court measure-evidence-capital-control-realization -- migrated from .github/workflows/measure-evidence-capital-control-realization.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile control-realization pack
echo "::group::measure-evidence-capital-control-realization: Compile control-realization pack"
(
set -e
python3 -m py_compile packs/evidence-capital-control-realization-pack/scripts/*.py packs/evidence-capital-control-realization-pack/tests/*.py
)
echo "::endgroup::"
# --- Run permanent control-realization courts
echo "::group::measure-evidence-capital-control-realization: Run permanent control-realization courts"
(
set -e
export PYTHONPATH="packs/evidence-capital-control-realization-pack"
python3 -m unittest discover -s packs/evidence-capital-control-realization-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-evidence-capital-control-realization: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/evidence-capital-control-realization-pack/scripts packs/evidence-capital-control-realization-pack/tests
)
echo "::endgroup::"
