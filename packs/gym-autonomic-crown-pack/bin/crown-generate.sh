#!/usr/bin/env bash
# Manufacture the gym-ecosystem autonomic crown receipt from real git observations.
#
# READ-ONLY with respect to git state. Writes ONLY into $WORKDIR (a scratch dir),
# never into the observed repository. Emitting the receipt into the repo, and any
# submodule checkout / lock rewrite / commit / push, stays with the superproject's
# GymAct/BRCE-admitted crown workflow -- this script has no such authority.
#
# Usage: crown-generate.sh <repo-root> <workdir> [--from-receipt <json>]
set -euo pipefail

PACK="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="${1:?usage: crown-generate.sh <repo-root> <workdir> [--from-receipt <json>]}"
WORKDIR="${2:?usage: crown-generate.sh <repo-root> <workdir> [--from-receipt <json>]}"
shift 2

mkdir -p "$WORKDIR/templates"
cp "$PACK/ggen.toml" "$WORKDIR/ggen.toml"
cp "$PACK"/templates/*.tmpl "$WORKDIR/templates/"
cat "$PACK/ontology.ttl" > "$WORKDIR/ontology.ttl"

if [[ "${1:-}" == "--from-receipt" ]]; then
  python3 "$PACK/bin/crown-observe.py" --from-receipt "$2" >> "$WORKDIR/ontology.ttl"
else
  python3 "$PACK/bin/crown-observe.py" --observe --root "$REPO" >> "$WORKDIR/ontology.ttl"
fi

python3 "$PACK/bin/run-gates.py" "$WORKDIR/ontology.ttl"

cd "$WORKDIR"
ggen sync run --format json >/dev/null 2>"$WORKDIR/ggen-sync.log"
echo "GYM_CROWN_GENERATED $WORKDIR/artifacts/autonomic-crown.json"

if [[ -f "$REPO/artifacts/autonomic-crown.json" ]]; then
  if diff -u "$REPO/artifacts/autonomic-crown.json" "$WORKDIR/artifacts/autonomic-crown.json"; then
    echo "GYM_CROWN_RECEIPT_IDENTICAL_ALIVE"
  else
    echo "GYM_CROWN_RECEIPT_DRIFT_OBSERVED (committed receipt is stale; actuation is not this script's authority)"
  fi
fi
