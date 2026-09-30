#!/usr/bin/env bash
# Court explore-opportunity-hypergraph-r30 -- migrated from .github/workflows/explore-opportunity-hypergraph-r30.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile permanent R30 court
echo "::group::explore-opportunity-hypergraph-r30: Compile permanent R30 court"
(
set -e
python3 -m py_compile packs/ggen-project-boundary-pack/tests/test_r30_opportunity_hypergraph.py
)
echo "::endgroup::"
# --- Execute permanent R30 court
echo "::group::explore-opportunity-hypergraph-r30: Execute permanent R30 court"
(
set -e
python3 packs/ggen-project-boundary-pack/tests/test_r30_opportunity_hypergraph.py -v
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::explore-opportunity-hypergraph-r30: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|urllib\.request\.(Request|urlopen)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/ggen-project-boundary-pack/tests/test_r30_opportunity_hypergraph.py
)
echo "::endgroup::"
