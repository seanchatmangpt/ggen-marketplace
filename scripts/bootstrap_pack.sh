#!/usr/bin/env bash
# bootstrap_pack.sh — driver for packs/pack-bootstrap-pack.
#
# Generates a new ggen pack (pack.toml, ontology.ttl, gates/, verify/,
# templates/registry.ex.eex) from a bootstrap INPUT ontology that declares
# one bp:BootstrapTarget plus the source classes to census.
#
# Usage:
#   scripts/bootstrap_pack.sh <input-ontology.ttl> <out-dir>
#
# Requires a built ggen_igniter checkout (MIX_ENV=dev mix compile done);
# GGEN_IGNITER_DIR overrides the path (default: ~/ggen_igniter).
# Read-only over this repo; no git operations.
set -euo pipefail

INPUT=${1:?usage: bootstrap_pack.sh <input-ontology.ttl> <out-dir>}
OUT=${2:?usage: bootstrap_pack.sh <input-ontology.ttl> <out-dir>}
GGEN_IGNITER_DIR=${GGEN_IGNITER_DIR:-"$HOME/ggen_igniter"}
PACK_DIR="$(cd "$(dirname "$0")/.." && pwd)/packs/pack-bootstrap-pack"

SYNC=(mix ggen_igniter.sync --pack-dir "$PACK_DIR" --ontology "$INPUT")

TEMPLATES=(
  "pack_toml:templates/pack_toml.eex:$OUT/pack.toml"
  "ontology:templates/ontology.eex:$OUT/ontology.ttl"
  "gate_census:templates/gate_census.eex:$OUT/gates/010_source_census.rq"
  "verify_census:templates/verify_census.eex:$OUT/verify/010_source_census.unbound.rq"
  "template_ontology:templates/template_ontology.eex:$OUT/templates/ontology.eex"
  "template_registry:templates/template_registry.eex:$OUT/templates/registry.ex.eex"
)

QUERIES=(
  --query meta=queries/meta.rq
  --query source_classes=queries/source_classes.rq
  --query source_properties=queries/source_properties.rq
  --query capability_rows=queries/capability_rows.rq
)

for entry in "${TEMPLATES[@]}"; do
  IFS=: read -r stem template out_path <<<"$entry"
  mkdir -p "$(dirname "$out_path")"
  (cd "$GGEN_IGNITER_DIR" && "${SYNC[@]}" "${QUERIES[@]}" \
    --template "$template" --out "$out_path")
  echo "wrote $out_path"
done

echo "bootstrap complete: $OUT (verify with the falsifier in packs/pack-bootstrap-pack/README.md)"
