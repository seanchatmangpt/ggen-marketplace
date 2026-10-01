#!/usr/bin/env bash
# Court measure-r66-current-consumer-independence -- migrated from .github/workflows/measure-r66-current-consumer-independence.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute fifty R54-derived independence courts on current heads
echo "::group::measure-r66-current-consumer-independence: Execute fifty R54-derived independence courts on current heads"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r54_consumer_independence.py
)
echo "::endgroup::"
# --- Verify R66 receipt authority and provenance
echo "::group::measure-r66-current-consumer-independence: Verify R66 receipt authority and provenance"
(
set -e
python3 - <<'PY'
import json
r=json.load(open('receipts/measure/2026-08-25-r66-current-independence-reconstitution.json'))
assert r['construction_base'] == '2fd796423c678e0b33e1828a5d187ca170e4eccc'
assert r['source_pr'] == 265
assert r['semantic_query_commits'] == 50
assert r['consequential_do'] is False
assert r['generated_output_edited'] is False
assert r['thousand_x']['standing'] == 'NOT_ADMITTED'
assert r['authority'] == 'OBSERVE|VERIFY|SELECT|CONSTRUCT'
print('R66_RECEIPT=PASS')
PY
)
echo "::endgroup::"
# --- Refuse ambient consequential DO
echo "::group::measure-r66-current-consumer-independence: Refuse ambient consequential DO"
(
set -e
! grep -R -E 'odrl:permission[^\n]*odrl:execute|actuationPerformed[[:space:]]+true' packs/epistemic-sensor-factory-pack/ontology/r54-consumer-independence.ttl packs/epistemic-sensor-factory-pack/fixtures/r54-consumer-independence-current.ttl
)
echo "::endgroup::"
