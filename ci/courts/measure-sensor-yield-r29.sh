#!/usr/bin/env bash
# Court measure-sensor-yield-r29 -- migrated from .github/workflows/measure-sensor-yield-r29.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile permanent R29 court
echo "::group::measure-sensor-yield-r29: Compile permanent R29 court"
(
set -e
python3 -m py_compile packs/ggen-project-boundary-pack/tests/test_r29_sensor_yield_calibration.py
)
echo "::endgroup::"
# --- Execute permanent R29 court
echo "::group::measure-sensor-yield-r29: Execute permanent R29 court"
(
set -e
python3 packs/ggen-project-boundary-pack/tests/test_r29_sensor_yield_calibration.py -v
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-sensor-yield-r29: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|urllib\.request\.(Request|urlopen)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/ggen-project-boundary-pack/tests/test_r29_sensor_yield_calibration.py
)
echo "::endgroup::"
