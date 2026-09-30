#!/usr/bin/env bash
# Court evolvable-capability-pack -- migrated from .github/workflows/evolvable-capability-pack.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute positive and negative gate witnesses
echo "::group::evolvable-capability-pack: Execute positive and negative gate witnesses"
(
set -e
python packs/evolvable-capability-pack/qualification/verify.py
)
echo "::endgroup::"
# --- Execute adversarial mutation court
echo "::group::evolvable-capability-pack: Execute adversarial mutation court"
(
set -e
python -m pytest tests/test_evolvable_capability_pack.py -v -p no:cacheprovider
)
echo "::endgroup::"
# --- Benchmark gate admission against the regression bound
echo "::group::evolvable-capability-pack: Benchmark gate admission against the regression bound"
(
set -e
python packs/evolvable-capability-pack/qualification/bench.py \
  --sizes 200,800 --repeats 3 --receipt "${RUNNER_TEMP}/evolvable-capability-bench.json"
)
echo "::endgroup::"
