#!/usr/bin/env bash
# Court measure-remediation-counterfactual-realization -- migrated from .github/workflows/measure-remediation-counterfactual-realization.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile realization runtime and courts
echo "::group::measure-remediation-counterfactual-realization: Compile realization runtime and courts"
(
set -e
python3 -m py_compile packs/owning-rail-remediation-counterfactual-realization-pack/scripts/*.py packs/owning-rail-remediation-counterfactual-realization-pack/tests/*.py
)
echo "::endgroup::"
# --- Run realization falsifier court
echo "::group::measure-remediation-counterfactual-realization: Run realization falsifier court"
(
set -e
python3 -m unittest discover -s packs/owning-rail-remediation-counterfactual-realization-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-remediation-counterfactual-realization: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/owning-rail-remediation-counterfactual-realization-pack/scripts packs/owning-rail-remediation-counterfactual-realization-pack/tests
)
echo "::endgroup::"
