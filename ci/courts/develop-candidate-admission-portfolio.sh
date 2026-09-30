#!/usr/bin/env bash
# Court develop-candidate-admission-portfolio -- migrated from .github/workflows/develop-candidate-admission-portfolio.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile pack runtime
echo "::group::develop-candidate-admission-portfolio: Compile pack runtime"
(
set -e
python3 -m py_compile packs/candidate-admission-portfolio-pack/scripts/*.py packs/candidate-admission-portfolio-pack/tests/*.py
)
echo "::endgroup::"
# --- Permanent courts
echo "::group::develop-candidate-admission-portfolio: Permanent courts"
(
set -e
PYTHONPATH=packs/candidate-admission-portfolio-pack python3 -m unittest discover -s packs/candidate-admission-portfolio-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- No ambient consequential actuation
echo "::group::develop-candidate-admission-portfolio: No ambient consequential actuation"
(
set -e
! grep -R -nE "requests\.(post|put|patch|delete)|subprocess\.|os\.system" packs/candidate-admission-portfolio-pack
)
echo "::endgroup::"
