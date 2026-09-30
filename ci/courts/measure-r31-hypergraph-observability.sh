#!/usr/bin/env bash
# Court measure-r31-hypergraph-observability -- migrated from .github/workflows/measure-r31-hypergraph-observability.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile permanent court
echo "::group::measure-r31-hypergraph-observability: Compile permanent court"
(
set -e
python3 -m py_compile packs/ggen-project-boundary-pack/tests/test_r31_hypergraph_observability.py
)
echo "::endgroup::"
# --- Execute permanent court
echo "::group::measure-r31-hypergraph-observability: Execute permanent court"
(
set -e
python3 packs/ggen-project-boundary-pack/tests/test_r31_hypergraph_observability.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r31-hypergraph-observability: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|urllib\.request\.(Request|urlopen)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/ggen-project-boundary-pack/tests/test_r31_hypergraph_observability.py
)
echo "::endgroup::"
