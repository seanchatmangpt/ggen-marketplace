#!/usr/bin/env bash
# Court develop-r71-orthogonal-consumer-capital -- migrated from .github/workflows/develop-r71-orthogonal-consumer-capital.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute 51 orthogonal consumer capital courts
echo "::group::develop-r71-orthogonal-consumer-capital: Execute 51 orthogonal consumer capital courts"
(
set -e
python3 packs/orthogonal-consumer-capital-pack/tests/test_contract.py
)
echo "::endgroup::"
# --- Verify construction receipt
echo "::group::develop-r71-orthogonal-consumer-capital: Verify construction receipt"
(
set -e
python3 - <<'PY'
import json
r=json.load(open('receipts/develop/2026-08-25-r71-orthogonal-consumer-capital.json'))
assert r['round'] == 'R71'
assert r['construction_base'] == '2469a38d0e7af8225bbd44693ad7256bc9efbf63'
assert r['semantic_query_commits'] == 51
assert r['minimum_new_meaningful_commits'] >= 57
assert r['consequential_do'] is False
assert r['generated_output_edited'] is False
assert r['thousand_x']['standing'] == 'NOT_ADMITTED'
print('R71_RECEIPT=PASS')
PY
)
echo "::endgroup::"
# --- Refuse ambient consequential DO
echo "::group::develop-r71-orthogonal-consumer-capital: Refuse ambient consequential DO"
(
set -e
set -euo pipefail
! grep -R -E 'occ:consequentialDo[[:space:]]+true' packs/orthogonal-consumer-capital-pack/ontology.ttl
! grep -E 'consequential_do[[:space:]]*=[[:space:]]*"(true|ALLOW)"' packs/orthogonal-consumer-capital-pack/pack.toml
)
echo "::endgroup::"
