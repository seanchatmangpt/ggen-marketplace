#!/usr/bin/env bash
# Court measure-r34-portfolio-observability -- migrated from .github/workflows/measure-r34-portfolio-observability.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Run portfolio contract court
echo "::group::measure-r34-portfolio-observability: Run portfolio contract court"
(
set -e
python3 -m unittest discover -s packs/portfolio-epistemic-observability-pack/tests -p 'test_*.py' -v
)
echo "::endgroup::"
# --- Enforce sensor surface
echo "::group::measure-r34-portfolio-observability: Enforce sensor surface"
(
set -e
test "$(find packs/portfolio-epistemic-observability-pack/queries -name '*.rq' | wc -l)" -ge 24
)
echo "::endgroup::"
# --- Refuse ambient actuation
echo "::group::measure-r34-portfolio-observability: Refuse ambient actuation"
(
set -e
! grep -REn 'requests\.(post|put|patch|delete)|subprocess\.|os\.system|boto3|azure\.|google\.cloud' packs/portfolio-epistemic-observability-pack
)
echo "::endgroup::"
