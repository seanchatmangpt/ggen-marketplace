#!/usr/bin/env bash
# Court develop-r68-control-plane-causality -- migrated from .github/workflows/develop-r68-control-plane-causality.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute fifty control-plane causality courts
echo "::group::develop-r68-control-plane-causality: Execute fifty control-plane causality courts"
(
set -e
python3 packs/control-plane-causality-observability-pack/tests/test_contract.py
)
echo "::endgroup::"
# --- Verify construction receipt authority
echo "::group::develop-r68-control-plane-causality: Verify construction receipt authority"
(
set -e
python3 - <<'PY'
import json
r=json.load(open('receipts/develop/2026-08-25-r68-control-plane-causality.json'))
assert r['round'] == 'R69'
assert r['construction_base'] == '95387a0632f7e460e65cdd89e77ea7f902093af0'
assert r['current_main_composition'] == '0377678f4741aadd5a40c5729ed016e163e3d4b2'
assert r['semantic_query_commits'] == 50
assert r['consequential_do'] is False
assert r['generated_output_edited'] is False
assert r['thousand_x']['standing'] == 'NOT_ADMITTED'
assert r['authority'] == 'OBSERVE|VERIFY|CONSTRUCT'
print('R69_RECEIPT=PASS')
PY
)
echo "::endgroup::"
# --- Refuse ambient consequential DO without rejecting falsifier courts
echo "::group::develop-r68-control-plane-causality: Refuse ambient consequential DO without rejecting falsifier courts"
(
set -e
set -euo pipefail
! grep -R -E 'actuationPerformed[[:space:]]+true' packs/control-plane-causality-observability-pack/ontology.ttl packs/control-plane-causality-observability-pack/fixtures
! grep -E 'consequential_do[[:space:]]*=[[:space:]]*"(true|ALLOW)"' packs/control-plane-causality-observability-pack/pack.toml
)
echo "::endgroup::"
