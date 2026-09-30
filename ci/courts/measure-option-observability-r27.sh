#!/usr/bin/env bash
# Court measure-option-observability-r27 -- migrated from .github/workflows/measure-option-observability-r27.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile permanent R27 court
echo "::group::measure-option-observability-r27: Compile permanent R27 court"
(
set -e
python3 -m py_compile packs/ggen-project-boundary-pack/tests/test_r27_option_observability.py
)
echo "::endgroup::"
# --- Execute permanent R27 court
echo "::group::measure-option-observability-r27: Execute permanent R27 court"
(
set -e
python3 packs/ggen-project-boundary-pack/tests/test_r27_option_observability.py -v
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-option-observability-r27: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|urllib\.request\.(Request|urlopen)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/ggen-project-boundary-pack/tests/test_r27_option_observability.py
)
echo "::endgroup::"
