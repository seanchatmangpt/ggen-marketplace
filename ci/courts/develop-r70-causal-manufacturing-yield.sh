#!/usr/bin/env bash
# Court develop-r70-causal-manufacturing-yield -- migrated from .github/workflows/develop-r70-causal-manufacturing-yield.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute extensible control-plane causality and yield courts
echo "::group::develop-r70-causal-manufacturing-yield: Execute extensible control-plane causality and yield courts"
(
set -e
python3 packs/control-plane-causality-observability-pack/tests/test_contract.py
)
echo "::endgroup::"
# --- Verify R70 construction receipt
echo "::group::develop-r70-causal-manufacturing-yield: Verify R70 construction receipt"
(
set -e
python3 - <<'PY'
import json
r=json.load(open('receipts/develop/2026-08-25-r70-causal-manufacturing-yield.json'))
assert r['round'] == 'R70'
assert r['construction_base'] == 'd92e65b761788c8ec18562d3d1183bce29c341f7'
assert r['semantic_query_commits'] == 50
assert r['minimum_new_semantic_commits'] >= 52
assert r['consequential_do'] is False
assert r['generated_output_edited'] is False
assert r['thousand_x']['standing'] == 'NOT_ADMITTED'
assert r['authority'] == 'OBSERVE|VERIFY|SELECT|CONSTRUCT'
print('R70_RECEIPT=PASS')
PY
)
echo "::endgroup::"
# --- Refuse ambient consequential DO
echo "::group::develop-r70-causal-manufacturing-yield: Refuse ambient consequential DO"
(
set -e
set -euo pipefail
! grep -R -E 'actuationPerformed[[:space:]]+true' packs/control-plane-causality-observability-pack/ontology.ttl packs/control-plane-causality-observability-pack/fixtures
! grep -E 'consequential_do[[:space:]]*=[[:space:]]*"(true|ALLOW)"' packs/control-plane-causality-observability-pack/pack.toml
)
echo "::endgroup::"
