#!/usr/bin/env bash
# Admitted Chicago sync court for issue-platform-controls-pack.
# Mounts real pack + scoped semantic-jira-pack (verify LAW only).
# Exit 0 = sync + replay green. Exit 2 = missing real SJ tree.
set -euo pipefail

PACK_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SJ_OUT="${1:-/tmp/ip-controls-sj-dep-court}"
SCRATCH="${2:-$(mktemp -d /tmp/ip-controls-sync-XXXXXX)}"

bash "$PACK_ROOT/qualification/materialize_sj_dep_court.sh" "$SJ_OUT" >/dev/null

mkdir -p "$SCRATCH/templates"
cat "$PACK_ROOT/ontology.ttl" "$PACK_ROOT/qualification/consumer.ttl" >"$SCRATCH/ontology.ttl"
# Unique local marker only — pack templates come from [packs] mount.
cat >"$SCRATCH/templates/zzz_scratch_marker.md.tera" <<'EOF'
---
to: "docs/generated/scratch-marker.md"
force: true
---
scratch admitted sync court
EOF

ln -sfn "$PACK_ROOT" "$SCRATCH/packs-ipc"
ln -sfn "$SJ_OUT" "$SCRATCH/packs-sj"

cat >"$SCRATCH/ggen.toml" <<'EOF'
[project]
name = "scratch-issue-platform-controls"

[ontology]
source = "ontology.ttl"

[packs]
issue-platform-controls-pack = { path = "packs-ipc" }
semantic-jira-pack = { path = "packs-sj" }

[templates]
dir = "templates"
EOF

(
  cd "$SCRATCH"
  ggen sync run --skip-ea-admission
  ggen sync run --skip-ea-admission
)
echo "ADMITTED_SYNC_OK scratch=$SCRATCH"
