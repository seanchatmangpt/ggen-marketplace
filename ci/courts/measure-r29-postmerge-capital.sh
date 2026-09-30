#!/usr/bin/env bash
# Court measure-r29-postmerge-capital -- migrated from .github/workflows/measure-r29-postmerge-capital.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile postmerge court
echo "::group::measure-r29-postmerge-capital: Compile postmerge court"
(
set -e
python3 -m py_compile packs/ggen-project-boundary-pack/tests/test_r29_postmerge_capital.py
)
echo "::endgroup::"
# --- Execute postmerge court
echo "::group::measure-r29-postmerge-capital: Execute postmerge court"
(
set -e
python3 packs/ggen-project-boundary-pack/tests/test_r29_postmerge_capital.py -v
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r29-postmerge-capital: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|urllib\.request\.(Request|urlopen)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/ggen-project-boundary-pack/tests/test_r29_postmerge_capital.py
)
echo "::endgroup::"
