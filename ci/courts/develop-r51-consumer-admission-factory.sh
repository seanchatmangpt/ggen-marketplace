#!/usr/bin/env bash
# Court develop-r51-consumer-admission-factory -- migrated from .github/workflows/develop-r51-consumer-admission-factory.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Run permanent R51 contract court
echo "::group::develop-r51-consumer-admission-factory: Run permanent R51 contract court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/test_r51_consumer_admission_factory.py
)
echo "::endgroup::"
# --- Execute all fifty R51 admission sensors
echo "::group::develop-r51-consumer-admission-factory: Execute all fifty R51 admission sensors"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r51_sparql.py
)
echo "::endgroup::"
# --- Validate receipt authority and 1000X refusal
echo "::group::develop-r51-consumer-admission-factory: Validate receipt authority and 1000X refusal"
(
set -e
python3 - <<'PY'
import json
p='receipts/develop/2026-08-25-r51-consumer-admission-factory.json'
r=json.load(open(p))
assert r['consequential_do'] is False
assert r['thousand_x']['standing'] == 'NOT_ADMITTED'
assert r['semantic_transitions']['sensors'] == 50
assert r['consumer_admission_shortfall'] == 8
print('R51_RECEIPT_AUTHORITY=PASS')
PY
)
echo "::endgroup::"
