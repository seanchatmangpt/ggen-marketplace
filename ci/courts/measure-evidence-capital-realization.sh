#!/usr/bin/env bash
# Court measure-evidence-capital-realization -- migrated from .github/workflows/measure-evidence-capital-realization.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile realization pack
echo "::group::measure-evidence-capital-realization: Compile realization pack"
(
set -e
python3.11 -m py_compile packs/evidence-capital-realization-pack/scripts/*.py packs/evidence-capital-realization-pack/tests/*.py
)
echo "::endgroup::"
# --- Run permanent realization courts
echo "::group::measure-evidence-capital-realization: Run permanent realization courts"
(
set -e
export PYTHONPATH="packs/evidence-capital-realization-pack"
python3.11 -m unittest discover -s packs/evidence-capital-realization-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-evidence-capital-realization: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|urllib\.request\.(Request|urlopen)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/evidence-capital-realization-pack/scripts packs/evidence-capital-realization-pack/tests
)
echo "::endgroup::"
