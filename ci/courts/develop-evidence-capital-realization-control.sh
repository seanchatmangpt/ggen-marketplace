#!/usr/bin/env bash
# Court develop-evidence-capital-realization-control -- migrated from .github/workflows/develop-evidence-capital-realization-control.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile controller
echo "::group::develop-evidence-capital-realization-control: Compile controller"
(
set -e
python3 -m py_compile packs/evidence-capital-realization-control-pack/scripts/*.py packs/evidence-capital-realization-control-pack/tests/*.py
)
echo "::endgroup::"
# --- Permanent courts
echo "::group::develop-evidence-capital-realization-control: Permanent courts"
(
set -e
export PYTHONPATH="packs/evidence-capital-realization-control-pack"
python3 -m unittest discover -s packs/evidence-capital-realization-control-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Refuse ambient consequential DO
echo "::group::develop-evidence-capital-realization-control: Refuse ambient consequential DO"
(
set -e
! grep -R -E "subprocess\.|os\.system|requests\.(post|put|patch|delete)" packs/evidence-capital-realization-control-pack/scripts packs/evidence-capital-realization-control-pack/tests
)
echo "::endgroup::"
