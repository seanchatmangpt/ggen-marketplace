#!/usr/bin/env bash
# Court develop-r67-current-consumer-independence -- migrated from .github/workflows/develop-r67-current-consumer-independence.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute fifty current independence courts
echo "::group::develop-r67-current-consumer-independence: Execute fifty current independence courts"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r67_consumer_independence.py
)
echo "::endgroup::"
# --- Verify construction receipt authority
echo "::group::develop-r67-current-consumer-independence: Verify construction receipt authority"
(
set -e
python3 - <<'PY'
import json
r=json.load(open('receipts/develop/2026-08-25-r67-current-independence-capital.json'))
assert r['construction_base'] == '5eac35d1a597080cab8388f4a72cb5278b3e4c92'
assert r['semantic_query_commits'] == 50
assert r['consequential_do'] is False
assert r['generated_output_edited'] is False
assert r['thousand_x']['standing'] == 'NOT_ADMITTED'
assert r['authority'] == 'OBSERVE|VERIFY|SELECT|CONSTRUCT'
print('R67_RECEIPT=PASS')
PY
)
echo "::endgroup::"
# --- Refuse ambient consequential DO
echo "::group::develop-r67-current-consumer-independence: Refuse ambient consequential DO"
(
set -e
! grep -R -E 'odrl:permission[^\n]*odrl:execute|actuationPerformed[[:space:]]+true' packs/epistemic-sensor-factory-pack/ontology/r67-consumer-independence.ttl packs/epistemic-sensor-factory-pack/fixtures/r67-consumer-independence-current.ttl
)
echo "::endgroup::"
