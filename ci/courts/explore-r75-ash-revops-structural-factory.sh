#!/usr/bin/env bash
# Court explore-r75-ash-revops-structural-factory -- migrated from .github/workflows/explore-r75-ash-revops-structural-factory.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute structural courts
echo "::group::explore-r75-ash-revops-structural-factory: Execute structural courts"
(
set -e
python3 -m unittest discover -s packs/ash-revops-structural-factory-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Verify deterministic surface
echo "::group::explore-r75-ash-revops-structural-factory: Verify deterministic surface"
(
set -e
test "$(find packs/ash-revops-structural-factory-pack/queries -name '*.rq' | wc -l)" -eq 23
test "$(find packs/ash-revops-structural-factory-pack/gates -name '*.rq' | wc -l)" -eq 4
test "$(find packs/ash-revops-structural-factory-pack/templates -name '*.tera' | wc -l)" -eq 7
)
echo "::endgroup::"
