#!/usr/bin/env bash
# Court develop-candidate-compatibility-portfolio -- migrated from .github/workflows/develop-candidate-compatibility-portfolio.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile pack algorithms
echo "::group::develop-candidate-compatibility-portfolio: Compile pack algorithms"
(
set -e
python3 -m py_compile packs/dfcm-pack/families/candidate-compatibility-portfolio/scripts/*.py packs/dfcm-pack/families/candidate-compatibility-portfolio/tests/*.py
)
echo "::endgroup::"
# --- Permanent courts
echo "::group::develop-candidate-compatibility-portfolio: Permanent courts"
(
set -e
export PYTHONPATH="packs/dfcm-pack/families/candidate-compatibility-portfolio"
python3 -m unittest discover -s packs/dfcm-pack/families/candidate-compatibility-portfolio/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Refuse ambient consequential DO
echo "::group::develop-candidate-compatibility-portfolio: Refuse ambient consequential DO"
(
set -e
! grep -R -E "subprocess\.|os\.system|requests\.(post|put|patch|delete)" packs/dfcm-pack/families/candidate-compatibility-portfolio/scripts packs/dfcm-pack/families/candidate-compatibility-portfolio/tests
)
echo "::endgroup::"
