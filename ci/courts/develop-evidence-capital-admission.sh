#!/usr/bin/env bash
# Court develop-evidence-capital-admission -- migrated from .github/workflows/develop-evidence-capital-admission.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile pack runtime
echo "::group::develop-evidence-capital-admission: Compile pack runtime"
(
set -e
python3 -m py_compile packs/evidence-capital-admission-pack/scripts/*.py packs/evidence-capital-admission-pack/tests/*.py
)
echo "::endgroup::"
# --- Permanent courts
echo "::group::develop-evidence-capital-admission: Permanent courts"
(
set -e
PYTHONPATH=packs/evidence-capital-admission-pack python3 -m unittest discover -s packs/evidence-capital-admission-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- No ambient consequential actuation
echo "::group::develop-evidence-capital-admission: No ambient consequential actuation"
(
set -e
! grep -R -nE "requests\.(post|put|patch|delete)|subprocess\.|os\.system" packs/evidence-capital-admission-pack
)
echo "::endgroup::"
