#!/bin/sh
# Gate 000 -- templates must not bake consumer bindings: module names,
# subject-id literals, or digest-algorithm literals. Every binding comes
# from fa:DossierConfig via queries/exporter.rq.
set -eu
cd "$(dirname "$0")/.."

hits=$(grep -rnE 'DossierExporter\.py|["'"'"']sha256["'"'"']|subject_id["'"'"'] *= *"|"FraudCase' templates/ | grep -v 'DIGEST_ALGORITHM = ' || true)
if [ -n "$hits" ]; then
  echo "gates/000 FAIL: hardcoded consumer bindings in templates/:" >&2
  echo "$hits" >&2
  exit 1
fi
echo "gates/000 ok: no hardcoded consumer bindings in templates/"
