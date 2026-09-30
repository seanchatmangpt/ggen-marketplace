#!/usr/bin/env bash
# Court measure-r56-combinatorial-consumer-portfolio -- migrated from .github/workflows/measure-r56-combinatorial-consumer-portfolio.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute fifty R56 combinatorial portfolio courts
echo "::group::measure-r56-combinatorial-consumer-portfolio: Execute fifty R56 combinatorial portfolio courts"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r56_combinatorial_consumer_portfolio.py
)
echo "::endgroup::"
# --- Verify R56 receipt and authority ceiling
echo "::group::measure-r56-combinatorial-consumer-portfolio: Verify R56 receipt and authority ceiling"
(
set -e
python3 - <<'PY'
import json
r=json.load(open('receipts/measure/2026-08-25-r56-combinatorial-consumer-portfolio.json'))
assert r['semantic_query_commits'] == 50
assert r['consequential_do'] is False
assert r['generated_output_edited'] is False
assert 'DO' not in r['authority']
assert r['source_generation'] == 'R55'
print('R56_RECEIPT=PASS')
PY
)
echo "::endgroup::"
