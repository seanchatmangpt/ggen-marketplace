#!/usr/bin/env bash
# Materialize a ggen-sync-safe SEMANTICS+LAW view of the real semantic-jira-pack.
#
# Why: ADR-0010 (ggen_igniter) scores gates/*.rq as witness-reporting
# (>=1 row = PASS). ggen 26.x FM-PACK-013 scores every pack gates/*.rq as
# offender-reporting (any row = refuse). Mounting the unscoped igniter tree
# under [packs] therefore false-fails on driver gates such as
# 010_work_order_subjects.rq (enumerates sj:WorkOrder subjects).
#
# This court does NOT weaken SJ execution law: it installs the real
# verify/*.unbound.rq offender queries as gates/*.rq (0 rows = PASS), keeps
# the real ontology.ttl, and omits witness-driver gates + full SJ projection
# templates (FM-PACK-005 satisfied by one court stub template).
#
# Usage:
#   qualification/materialize_sj_dep_court.sh [OUT_DIR]
# Default OUT_DIR: /tmp/ip-controls-sj-dep-court
# Exit 2 if the pinned real semantic-jira-pack tree is absent.

set -euo pipefail

REAL_SJ="${GGEN_SEMANTIC_JIRA_PACK:-$HOME/ggen_igniter/priv/ggen/semantic-jira-pack}"
OUT="${1:-/tmp/ip-controls-sj-dep-court}"

if [[ ! -d "$REAL_SJ" || ! -f "$REAL_SJ/ontology.ttl" ]]; then
  echo "BLOCKED:missing-semantic-jira-pack path=$REAL_SJ" >&2
  exit 2
fi
if [[ ! -d "$REAL_SJ/verify" ]]; then
  echo "BLOCKED:missing-semantic-jira-verify path=$REAL_SJ/verify" >&2
  exit 2
fi

rm -rf "$OUT"
mkdir -p "$OUT/gates" "$OUT/templates"

# Real ontology (byte-identical to pinned tree).
cp -f "$REAL_SJ/ontology.ttl" "$OUT/ontology.ttl"

# Scope dep LAW gates to SJ offender-reporting verify companions only.
# Strip the .unbound suffix so ggen discovers them as gates/*.rq.
shopt -s nullglob
unbound=("$REAL_SJ"/verify/*.unbound.rq)
if ((${#unbound[@]} == 0)); then
  echo "BLOCKED:empty-semantic-jira-verify path=$REAL_SJ/verify" >&2
  exit 2
fi
for src in "${unbound[@]}"; do
  base="$(basename "$src" .unbound.rq)"
  cp -f "$src" "$OUT/gates/${base}.rq"
done
shopt -u nullglob

# Minimal template — court must not re-project the SJ backlog.
cat > "$OUT/templates/000_sj_dep_court_stub.md.tera" <<'EOF'
---
to: "docs/generated/sj-dep-court-stub.md"
force: true
---
# semantic-jira-pack dep court (SEMANTICS + verify LAW)

Scoped materialization for issue-platform-controls-pack qualification.
Witness-driver gates/ omitted (ADR-0010 ≠ FM-PACK-013). Offender verify/
gates installed under gates/*.rq.
EOF

# Identity + capability URN. Version mirrors the real pack.toml when present.
SJ_VER="0.0.0-court-scoped"
if [[ -f "$REAL_SJ/pack.toml" ]]; then
  parsed="$(awk -F'"' '/^version[[:space:]]*=/ {print $2; exit}' "$REAL_SJ/pack.toml" || true)"
  if [[ -n "$parsed" ]]; then
    SJ_VER="${parsed}-court-scoped"
  fi
fi

cat > "$OUT/pack.toml" <<EOF
[pack]
name = "semantic-jira-pack"
version = "${SJ_VER}"
description = """Court-scoped SEMANTICS+LAW view of ${REAL_SJ}.
ontology.ttl is a byte copy of the real pack. gates/*.rq are the real
verify/*.unbound.rq offender queries (ADR-0010), renamed for ggen
FM-PACK-013. Witness-driver gates/ and full projection templates are
intentionally omitted so overlay sync is not false-refused."""

[capabilities]
provides = ["urn:ggen:pack:semantic-jira-pack"]
requires = []

[validation]
gates = [
$(for f in "$OUT"/gates/*.rq; do echo "  \"gates/$(basename "$f")\","; done | sed '$ s/,$//')
]
EOF

# Provenance stamp for the court receipt.
{
  echo "real_sj_path=${REAL_SJ}"
  echo "ontology_sha256=$(shasum -a 256 "$OUT/ontology.ttl" | awk '{print $1}')"
  echo "gate_count=$(find "$OUT/gates" -name '*.rq' | wc -l | tr -d ' ')"
  echo "materialized_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$OUT/COURT_STAMP.txt"

echo "$OUT"
