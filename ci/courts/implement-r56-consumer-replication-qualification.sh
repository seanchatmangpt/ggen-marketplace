#!/usr/bin/env bash
# Court implement-r56-consumer-replication-qualification -- migrated from .github/workflows/implement-r56-consumer-replication-qualification.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute fifty R56 consumer replication courts
echo "::group::implement-r56-consumer-replication-qualification: Execute fifty R56 consumer replication courts"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r56_consumer_replication_qualification.py
)
echo "::endgroup::"
# --- Verify manufacture receipt
echo "::group::implement-r56-consumer-replication-qualification: Verify manufacture receipt"
(
set -e
python3 - <<'PY'
import json
r=json.load(open('receipts/implement/2026-08-25-r56-consumer-replication-qualification.json'))
assert r['semantic_query_commits'] == 50
assert r['consequential_do'] is False
assert r['generated_output_edited'] is False
assert r['replication_multiplier']['R_qualification'] == 50
assert r['thousand_x']['standing'] == 'NOT_ADMITTED'
assert 'DO' not in r['authority']
print('R56_RECEIPT=PASS')
PY
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::implement-r56-consumer-replication-qualification: Refuse ambient consequential actuation"
(
set -e
set -euo pipefail
! grep -R -nE 'kubectl apply|terraform apply|aws .*create|gcloud .*create|az .*create' packs/epistemic-sensor-factory-pack/queries/ packs/epistemic-sensor-factory-pack/tests/run_r56_consumer_replication_qualification.py
)
echo "::endgroup::"
