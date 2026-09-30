#!/usr/bin/env bash
# Court measure-r53-causal-propagation -- migrated from .github/workflows/measure-r53-causal-propagation.yml
# Pure verification; no network, no mutation. Run from repo root.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
# --- Execute dependency-free static contract
echo "::group::measure-r53-causal-propagation: Execute dependency-free static contract"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/test_r53_static_contract.py
)
echo "::endgroup::"
# --- Execute dependency-free RDF court and all 50 sensors
echo "::group::measure-r53-causal-propagation: Execute dependency-free RDF court and all 50 sensors"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/test_r53_causal_propagation.py
)
echo "::endgroup::"
# --- Enforce documentation/runtime correspondence
echo "::group::measure-r53-causal-propagation: Enforce documentation/runtime correspondence"
(
set -e
python3 packs/epistemic-sensor-factory-pack/tests/test_r53_doc_runtime_correspondence.py
)
echo "::endgroup::"
# --- Refuse ambient consequential actuation
echo "::group::measure-r53-causal-propagation: Refuse ambient consequential actuation"
(
set -eo pipefail
! grep -R --include='*.ttl' --include='*.json' --include='*.tera' -E 'actuationPerformed[[:space:]]+true|"consequential_do"[[:space:]]*:[[:space:]]*true|standingTransferred[[:space:]]+true|authorityTransferred[[:space:]]+true' packs/epistemic-sensor-factory-pack/fixtures packs/epistemic-sensor-factory-pack/templates
)
echo "::endgroup::"
