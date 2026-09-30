#!/usr/bin/env bash
# Court measure-r50-consumer-evidence-return -- migrated from .github/workflows/measure-r50-consumer-evidence-return.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Run permanent R50 contract court
echo "::group::measure-r50-consumer-evidence-return: Run permanent R50 contract court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/test_r50_consumer_evidence_return.py
)
echo "::endgroup::"
# --- Execute all fifty R50 sensors
echo "::group::measure-r50-consumer-evidence-return: Execute all fifty R50 sensors"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r50_sparql.py
)
echo "::endgroup::"
# --- Validate receipt authority
echo "::group::measure-r50-consumer-evidence-return: Validate receipt authority"
(
set -e
python3 - <<'PY'
import json
p='receipts/measure/2026-08-25-r50-consumer-evidence-return.json'
r=json.load(open(p))
assert r['consequential_do'] is False
assert r['thousand_x']['standing'] == 'NOT_ADMITTED'
assert r['semantic_transitions']['sensors'] == 50
print('R50_RECEIPT_AUTHORITY=PASS')
PY
)
echo "::endgroup::"
