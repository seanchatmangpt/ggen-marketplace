#!/usr/bin/env bash
# Court measure-r61-consumer-receipt-assimilation -- migrated from .github/workflows/measure-r61-consumer-receipt-assimilation.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute R61 permanent court
echo "::group::measure-r61-consumer-receipt-assimilation: Execute R61 permanent court"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/run_r61_consumer_receipt_assimilation.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r61-consumer-receipt-assimilation: Refuse ambient consequential actuation"
(
set -eo pipefail
grep -q 'consequentialDo "PROHIBITED"' packs/epistemic-sensor-factory-pack/ontology.r61-consumer-receipt-assimilation.ttl
grep -q '"consequential_do":false' receipts/measure/2026-08-25-r61-consumer-receipt-assimilation.json
)
echo "::endgroup::"
