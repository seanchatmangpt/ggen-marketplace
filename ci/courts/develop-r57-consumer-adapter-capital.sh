#!/usr/bin/env bash
# Court develop-r57-consumer-adapter-capital -- migrated from .github/workflows/develop-r57-consumer-adapter-capital.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute fifty R57 consumer adapter-capital courts
echo "::group::develop-r57-consumer-adapter-capital: Execute fifty R57 consumer adapter-capital courts"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r57_consumer_adapter_capital.py
)
echo "::endgroup::"
# --- Verify manufacture receipt
echo "::group::develop-r57-consumer-adapter-capital: Verify manufacture receipt"
(
set -e
python3 - <<'PY'
import json
r=json.load(open('receipts/develop/2026-08-25-r57-consumer-adapter-capital.json'))
assert r['semantic_query_commits'] == 50
assert r['consequential_do'] is False
assert r['generated_output_edited'] is False
assert r['consumer_count'] == 4
assert r['consumer_families'] == 4
assert r['full_adapter_ready'] == 2
assert r['consumer_shortfall'] == 8
assert r['thousand_x']['standing'] == 'NOT_ADMITTED'
assert 'DO' not in r['authority']
print('R57_RECEIPT=PASS')
PY
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::develop-r57-consumer-adapter-capital: Refuse ambient consequential actuation"
(
set -e
set -euo pipefail
! grep -R -nE 'kubectl apply|terraform apply|aws .*create|gcloud .*create|az .*create' packs/epistemic-sensor-factory-pack/queries/ packs/epistemic-sensor-factory-pack/tests/run_r57_consumer_adapter_capital.py
)
echo "::endgroup::"
