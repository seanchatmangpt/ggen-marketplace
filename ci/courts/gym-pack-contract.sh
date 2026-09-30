#!/usr/bin/env bash
# Court gym-pack-contract -- migrated from .github/workflows/gym-pack-contract.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Compile deterministic court
echo "::group::gym-pack-contract: Compile deterministic court"
(
set -e
python3 -m py_compile scripts/verify-gym-packs.py
)
echo "::endgroup::"
# --- Manufacture receipt twice
echo "::group::gym-pack-contract: Manufacture receipt twice"
(
set -e
python3 scripts/verify-gym-packs.py --receipt ${RUNNER_TEMP}/gym-receipt-a.json
python3 scripts/verify-gym-packs.py --receipt ${RUNNER_TEMP}/gym-receipt-b.json
cmp ${RUNNER_TEMP}/gym-receipt-a.json ${RUNNER_TEMP}/gym-receipt-b.json
)
echo "::endgroup::"
# --- Replay exact receipt
echo "::group::gym-pack-contract: Replay exact receipt"
(
set -e
python3 scripts/verify-gym-packs.py --replay ${RUNNER_TEMP}/gym-receipt-a.json
)
echo "::endgroup::"
# --- Execute mutation falsifiers
echo "::group::gym-pack-contract: Execute mutation falsifiers"
(
set -e
python3 scripts/verify-gym-packs.py --self-test
)
echo "::endgroup::"
