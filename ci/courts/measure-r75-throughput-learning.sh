#!/usr/bin/env bash
# Court measure-r75-throughput-learning -- migrated from .github/workflows/measure-r75-throughput-learning.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute R75 court
echo "::group::measure-r75-throughput-learning: Execute R75 court"
(
set -e
pytest -q packs/epistemic-sensor-factory-pack/tests/test_r75_throughput_learning.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r75-throughput-learning: Refuse ambient consequential actuation"
(
set -e
if grep -R -nE 'actuationPerformed[[:space:]]+true|consequential_do[[:space:]]*[:=][[:space:]]*true' packs/epistemic-sensor-factory-pack/ontology.r75-throughput-learning.ttl packs/epistemic-sensor-factory-pack/fixtures/r75-throughput-learning.ttl; then exit 1; fi
)
echo "::endgroup::"
