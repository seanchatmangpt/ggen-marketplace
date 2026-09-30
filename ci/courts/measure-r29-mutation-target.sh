#!/usr/bin/env bash
# Court measure-r29-mutation-target -- migrated from .github/workflows/measure-r29-mutation-target.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile permanent court
echo "::group::measure-r29-mutation-target: Compile permanent court"
(
set -e
python3 -m py_compile packs/ggen-project-boundary-pack/tests/test_r29_mutation_target_correspondence.py
)
echo "::endgroup::"
# --- Execute permanent court
echo "::group::measure-r29-mutation-target: Execute permanent court"
(
set -e
python3 packs/ggen-project-boundary-pack/tests/test_r29_mutation_target_correspondence.py -v
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r29-mutation-target: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|urllib\.request\.(Request|urlopen)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/ggen-project-boundary-pack/tests/test_r29_mutation_target_correspondence.py
)
echo "::endgroup::"
