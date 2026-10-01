#!/usr/bin/env bash
# Court measure-owning-rail-remediation-realization -- migrated from .github/workflows/measure-owning-rail-remediation-realization.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile runtime measurement substrate
echo "::group::measure-owning-rail-remediation-realization: Compile runtime measurement substrate"
(
set -e
python3 -m py_compile packs/owning-rail-remediation-realization-pack/scripts/*.py packs/owning-rail-remediation-realization-pack/tests/*.py
)
echo "::endgroup::"
# --- Run remediation realization courts
echo "::group::measure-owning-rail-remediation-realization: Run remediation realization courts"
(
set -e
python3 -m unittest discover -s packs/owning-rail-remediation-realization-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-owning-rail-remediation-realization: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|subprocess\.|os\.system|boto3|azure\.|google\.cloud|socket\.' packs/owning-rail-remediation-realization-pack/scripts packs/owning-rail-remediation-realization-pack/tests
)
echo "::endgroup::"
