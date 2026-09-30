#!/usr/bin/env bash
# Court measure-r54-consumer-independence -- migrated from .github/workflows/measure-r54-consumer-independence.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute fifty R54 independence courts
echo "::group::measure-r54-consumer-independence: Execute fifty R54 independence courts"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r54_consumer_independence.py
)
echo "::endgroup::"
# --- Verify R54 receipt authority
echo "::group::measure-r54-consumer-independence: Verify R54 receipt authority"
(
set -e
python3 - <<'PY'
import json
r=json.load(open('receipts/measure/2026-08-25-r54-consumer-independence.json'))
assert r['semantic_query_commits'] == 50
assert r['consequential_do'] is False
assert r['generated_output_edited'] is False
assert r['thousand_x']['standing'] == 'NOT_ADMITTED'
assert r['authority'] == 'OBSERVE|VERIFY|SELECT|CONSTRUCT'
print('R54_RECEIPT=PASS')
PY
)
echo "::endgroup::"
