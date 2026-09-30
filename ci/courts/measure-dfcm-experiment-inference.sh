#!/usr/bin/env bash
# Court measure-dfcm-experiment-inference -- migrated from .github/workflows/measure-dfcm-experiment-inference.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Require complete inference court
echo "::group::measure-dfcm-experiment-inference: Require complete inference court"
(
set -e
test "$(find packs/dfcm-maximalist-court-pack/queries -maxdepth 1 -name 'inference-*.rq' | wc -l)" -ge 30
grep -RIl 'ExperimentRealization' packs/dfcm-maximalist-court-pack/queries/inference-*.rq >/dev/null
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-dfcm-experiment-inference: Refuse ambient consequential actuation"
(
set -e
! grep -REn 'curl |wget |gh |requests\.(post|put|patch|delete)|subprocess\.|os\.system' packs/dfcm-maximalist-court-pack/queries/inference-*.rq
)
echo "::endgroup::"
