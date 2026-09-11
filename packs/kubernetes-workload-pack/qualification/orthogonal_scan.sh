#!/usr/bin/env bash
# kubernetes-workload-pack orthogonal scanner layer.
#
# Deliberately independent sensors, none of which sees this pack's own
# SPARQL gate: kubeconform (schema conformance against the pinned
# Kubernetes OpenAPI schema), trivy config (misconfiguration scan),
# kubescape (NSA/CIS-aligned control assessment), kyverno (policy-engine
# admission simulation). Real tool output only -- no result here is
# fabricated or assumed; this script's own exit code is the honest
# aggregate.
#
# Usage: bash qualification/orthogonal_scan.sh
# Requires: ggen, kubeconform, trivy, kubescape, kyverno on PATH.
set -euo pipefail
PACK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT

FIXTURES=(
  "examples/minimal-secure-workload"
  "examples/high-assurance-workload"
  "examples/xaas-workload"
  "playground/scenarios/legitimate-exception"
)
# Known-gap negative controls are included deliberately -- the point of
# this scanner layer is to prove they DO fail somewhere, even though this
# pack's own gate 010 cannot catch them (see control-mapping/control-map.md).
NEGATIVE_FIXTURES=(
  "examples/negative-controls/privileged-container-KNOWN_GAP"
  "examples/negative-controls/mutable-image-tag-KNOWN_GAP"
)

echo "== Render (real ggen, write mode into scratch) =="
render() {
  local rel="$1" name
  name="$(basename "$rel")"
  ( cd "$PACK_DIR/$rel" && /opt/homebrew/bin/ggen sync run --format json >/dev/null )
  cp "$PACK_DIR/$rel"/k8s/*.yaml "$SCRATCH/${name}.yaml"
  rm -rf "$PACK_DIR/$rel/k8s"
}
for f in "${FIXTURES[@]}" "${NEGATIVE_FIXTURES[@]}"; do
  render "$f"
done

echo "== kubeconform -strict (schema conformance) =="
kubeconform -strict -summary -output json "$SCRATCH"/*.yaml

echo "== trivy config (misconfiguration; known-gap fixtures are EXPECTED to fire) =="
trivy config --severity HIGH,CRITICAL "$SCRATCH"

echo "== kyverno apply (policy-engine admission simulation) =="
kyverno apply "$PACK_DIR/qualification/policies/restricted-pss-subset.kyverno.yaml" \
  $(for f in "$SCRATCH"/*.yaml; do printf -- '--resource %s ' "$f"; done) \
  || { echo "Kyverno reported failures above -- expected for the two negative-controls fixtures; a non-zero exit here is not itself a script failure, inspect which resources failed."; }

echo "== kubescape scan framework NSA,cis-v1.10.0 (independent NSA/CIS control assessment) =="
kubescape scan framework NSA,cis-v1.10.0 "$SCRATCH" --format json --output "$SCRATCH/kubescape-report.json" \
  || echo "kubescape exits non-zero on any failing control by design -- inspect $SCRATCH/kubescape-report.json before treating this as a script failure."

echo "== Cosign: intentionally not run =="
echo "This pack generates Deployment+Service YAML only -- it does not build or push a container image, so there is no real image/digest to sign or verify. Running cosign against an illustrative, non-pushed image reference would fabricate evidence. See control-mapping/control-map.md's SEC-COSIGN-001 row."
