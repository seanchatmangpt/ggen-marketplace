#!/usr/bin/env bash
# Court develop-selection-evidence-acquisition -- migrated from .github/workflows/develop-selection-evidence-acquisition.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile acquisition substrate
echo "::group::develop-selection-evidence-acquisition: Compile acquisition substrate"
(
set -e
python3 -m compileall -q packs/dfcm-pack/families/selection-evidence-acquisition/scripts packs/dfcm-pack/families/selection-evidence-acquisition/tests
)
echo "::endgroup::"
# --- Execute acquisition court
echo "::group::develop-selection-evidence-acquisition: Execute acquisition court"
(
set -e
python3 -m unittest discover -s packs/dfcm-pack/families/selection-evidence-acquisition/tests -p 'test_*.py' -v
)
echo "::endgroup::"
