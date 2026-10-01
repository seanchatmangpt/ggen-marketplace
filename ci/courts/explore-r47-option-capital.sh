#!/usr/bin/env bash
# Court explore-r47-option-capital -- migrated from .github/workflows/explore-r47-option-capital.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Run recombination courts
echo "::group::explore-r47-option-capital: Run recombination courts"
(
set -e
python3 -m unittest discover -s packs/option-capital-recombination-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Verify option machinery breadth
echo "::group::explore-r47-option-capital: Verify option machinery breadth"
(
set -e
test "$(find packs/option-capital-recombination-pack/queries -name '*.rq' | wc -l)" -ge 25
test "$(find packs/option-capital-recombination-pack/gates -name '*.rq' | wc -l)" -ge 10
test "$(find packs/option-capital-recombination-pack/templates -name '*.tera' | wc -l)" -ge 4
)
echo "::endgroup::"
