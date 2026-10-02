#!/usr/bin/env bash
# Court develop-process-methodology-closure-r3 -- migrated from .github/workflows/develop-process-methodology-closure-r3.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Verify eleven methodology projections
echo "::group::develop-process-methodology-closure-r3: Verify eleven methodology projections"
(
set -e
test "$(find packs/dfcm-pack/families/maximalist-court/queries -maxdepth 1 -name 'develop-method-*.rq' | wc -l)" -ge 11
)
echo "::endgroup::"
# --- Verify selection authority receipt
echo "::group::develop-process-methodology-closure-r3: Verify selection authority receipt"
(
set -e
python3 -c "import json; d=json.load(open('receipts/select/2026-08-24-process-methodology-closure-r3.json')); assert d['authority']=='SELECT' and d['actuation_performed'] is False and d['marketplace_first'] is True"
)
echo "::endgroup::"
