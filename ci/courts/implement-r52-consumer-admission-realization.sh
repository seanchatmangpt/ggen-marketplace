#!/usr/bin/env bash
# Court implement-r52-consumer-admission-realization -- migrated from .github/workflows/implement-r52-consumer-admission-realization.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute fifty R52 admission-realization courts
echo "::group::implement-r52-consumer-admission-realization: Execute fifty R52 admission-realization courts"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r52_admission_realization.py
)
echo "::endgroup::"
# --- Verify manufacture receipt
echo "::group::implement-r52-consumer-admission-realization: Verify manufacture receipt"
(
set -e
python3 - <<'PY'
import json
r=json.load(open('receipts/implement/2026-08-25-r52-consumer-admission-realization.json'))
assert r['semantic_query_commits'] == 50
assert r['consequential_do'] is False
assert r['generated_output_edited'] is False
assert r['thousand_x']['standing'] == 'NOT_ADMITTED'
print('R52_RECEIPT=PASS')
PY
)
echo "::endgroup::"
