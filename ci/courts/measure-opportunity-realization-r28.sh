#!/usr/bin/env bash
# Court measure-opportunity-realization-r28 -- migrated from .github/workflows/measure-opportunity-realization-r28.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile permanent R28 court
echo "::group::measure-opportunity-realization-r28: Compile permanent R28 court"
(
set -e
python3 -m py_compile packs/ggen-project-boundary-pack/tests/test_r28_opportunity_realization.py
)
echo "::endgroup::"
# --- Execute permanent R28 court
echo "::group::measure-opportunity-realization-r28: Execute permanent R28 court"
(
set -e
python3 packs/ggen-project-boundary-pack/tests/test_r28_opportunity_realization.py -v
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-opportunity-realization-r28: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|urllib\.request\.(Request|urlopen)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/ggen-project-boundary-pack/tests/test_r28_opportunity_realization.py
)
echo "::endgroup::"
