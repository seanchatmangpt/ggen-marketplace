#!/usr/bin/env bash
# Court measure-r51-transitive-propagation -- migrated from .github/workflows/measure-r51-transitive-propagation.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute permanent R51 court and all 50 sensors
echo "::group::measure-r51-transitive-propagation: Execute permanent R51 court and all 50 sensors"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/test_r51_transitive_propagation.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r51-transitive-propagation: Refuse ambient consequential actuation"
(
set -eo pipefail
! grep -R --include='*.ttl' --include='*.json' -E 'actuationPerformed[[:space:]]+true|"consequential_do"[[:space:]]*:[[:space:]]*true' packs/epistemic-sensor-factory-pack/fixtures packs/epistemic-sensor-factory-pack/templates
)
echo "::endgroup::"
