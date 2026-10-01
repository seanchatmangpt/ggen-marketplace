#!/usr/bin/env bash
# Court measure-evidence-lineage-independence -- migrated from .github/workflows/measure-evidence-lineage-independence.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile measurement court
echo "::group::measure-evidence-lineage-independence: Compile measurement court"
(
set -e
python3 -m py_compile packs/evidence-lineage-independence-pack/scripts/*.py packs/evidence-lineage-independence-pack/tests/*.py
)
echo "::endgroup::"
# --- Run permanent falsifiers
echo "::group::measure-evidence-lineage-independence: Run permanent falsifiers"
(
set -e
export PYTHONPATH="packs/evidence-lineage-independence-pack"
python3 -m unittest discover -s packs/evidence-lineage-independence-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-evidence-lineage-independence: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|urllib\.request\.(Request|urlopen)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/evidence-lineage-independence-pack/scripts packs/evidence-lineage-independence-pack/tests
)
echo "::endgroup::"
