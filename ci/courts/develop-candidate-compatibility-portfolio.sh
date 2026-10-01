#!/usr/bin/env bash
# Court develop-candidate-compatibility-portfolio -- migrated from .github/workflows/develop-candidate-compatibility-portfolio.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile pack algorithms
echo "::group::develop-candidate-compatibility-portfolio: Compile pack algorithms"
(
set -e
python3 -m py_compile packs/dfcm-candidate-compatibility-portfolio-pack/scripts/*.py packs/dfcm-candidate-compatibility-portfolio-pack/tests/*.py
)
echo "::endgroup::"
# --- Permanent courts
echo "::group::develop-candidate-compatibility-portfolio: Permanent courts"
(
set -e
export PYTHONPATH="packs/dfcm-candidate-compatibility-portfolio-pack"
python3 -m unittest discover -s packs/dfcm-candidate-compatibility-portfolio-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Refuse ambient consequential DO
echo "::group::develop-candidate-compatibility-portfolio: Refuse ambient consequential DO"
(
set -e
! grep -R -E "subprocess\.|os\.system|requests\.(post|put|patch|delete)" packs/dfcm-candidate-compatibility-portfolio-pack/scripts packs/dfcm-candidate-compatibility-portfolio-pack/tests
)
echo "::endgroup::"
