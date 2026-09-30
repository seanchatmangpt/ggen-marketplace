#!/usr/bin/env bash
# Court develop-selection-robustness-r3 -- migrated from .github/workflows/develop-selection-robustness-r3.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Verify selection authority receipt
echo "::group::develop-selection-robustness-r3: Verify selection authority receipt"
(
set -e
python3 -c "import json; d=json.load(open('receipts/select/2026-08-24-selection-robustness-r3.json')); assert d['authority']=='SELECT' and d['actuation_performed'] is False and d['marketplace_first'] is True"
)
echo "::endgroup::"
