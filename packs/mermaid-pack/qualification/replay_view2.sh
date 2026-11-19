#!/bin/sh
# FNOX-SJ-VIEW-2 replay: aoq-pack ontology -> mermaid-pack C4 templates -> mermaid.parse.
# aoq-pack is READ-ONLY: everything runs on a scratch copy.
# Env: GGEN (default ggen), MERMAID_NODE_MODULES (dir holding mermaid + jsdom; default
# srve servengine-frontend node_modules).
set -u
PACK="$(cd "$(dirname "$0")/.." && pwd)"
AOQ="$PACK/../aoq-pack/ontology.ttl"
GGEN="${GGEN:-ggen}"
NM="${MERMAID_NODE_MODULES:-/Users/sac/srve/servengine-frontend/node_modules}"
[ -f "$AOQ" ] || { echo "MISSING $AOQ"; exit 2; }
[ -d "$NM/mermaid" ] || { echo "MISSING mermaid in $NM"; exit 2; }

W="$(mktemp -d)"
trap 'rm -rf "$W"' EXIT

setup() { # $1 = dir
  d="$1"; mkdir -p "$d/templates" "$d/ontology"
  cp "$PACK/templates/aoq_c4_context.mmd.tmpl" "$PACK/templates/aoq_c4_containers.mmd.tmpl" \
     "$PACK/templates/verify_mermaid.mjs.tmpl" "$d/templates/"
  cat "$AOQ" "$PACK/c4/aoq-c4-map.ttl" > "$d/ontology/model.ttl"
  # Rule queries bind one top-level array `results` (see premature-actuation-survival-pack).
  # One query per rule: rows carry ?rt ("node"|"edge"|"container") and the templates filter on it.
  mkdir -p "$d/queries"
  cat > "$d/queries/c4_context.rq" <<'EOF'
PREFIX c4: <https://seanchatmangpt.github.io/ontology/c4#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?rt ?id ?label ?kind ?from ?to ?rel WHERE {
  {
    { ?s a c4:Person . BIND("Person" AS ?kind) }
    UNION
    { ?s a c4:SoftwareSystem . BIND("System" AS ?kind) }
    ?s rdfs:label ?label .
    BIND("node" AS ?rt)
    BIND(IF(STR(?s) = "urn:aoq:", "aoq", STRAFTER(STR(?s), "urn:aoq:")) AS ?id)
  }
  UNION
  {
    ?a c4:uses ?b .
    { ?a a c4:Person } UNION { ?a a c4:SoftwareSystem }
    { ?b a c4:Person } UNION { ?b a c4:SoftwareSystem }
    OPTIONAL { ?a c4:relLabel ?r }
    BIND("edge" AS ?rt)
    BIND(IF(STR(?a) = "urn:aoq:", "aoq", STRAFTER(STR(?a), "urn:aoq:")) AS ?from)
    BIND(IF(STR(?b) = "urn:aoq:", "aoq", STRAFTER(STR(?b), "urn:aoq:")) AS ?to)
    BIND(COALESCE(?r, "uses") AS ?rel)
  }
} ORDER BY ?rt ?id ?from ?to
EOF
  cat > "$d/queries/c4_containers.rq" <<'EOF'
PREFIX c4: <https://seanchatmangpt.github.io/ontology/c4#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?rt ?id ?label ?tech ?sys ?from ?to ?rel WHERE {
  {
    ?s a c4:Container ;
       rdfs:label ?label ;
       c4:inSystem ?sysIri .
    OPTIONAL { ?s c4:technology ?t }
    BIND("container" AS ?rt)
    BIND(STRAFTER(STR(?s), "urn:aoq:") AS ?id)
    BIND(IF(STR(?sysIri) = "urn:aoq:", "aoq", STRAFTER(STR(?sysIri), "urn:aoq:")) AS ?sys)
    BIND(COALESCE(?t, "") AS ?tech)
  }
  UNION
  {
    ?a c4:uses ?b .
    ?a a c4:Container .
    ?b a c4:Container .
    OPTIONAL { ?a c4:relLabel ?r }
    BIND("edge" AS ?rt)
    BIND(STRAFTER(STR(?a), "urn:aoq:") AS ?from)
    BIND(STRAFTER(STR(?b), "urn:aoq:") AS ?to)
    BIND(COALESCE(?r, "uses") AS ?rel)
  }
} ORDER BY ?rt ?sys ?id ?from ?to
EOF
  cat > "$d/queries/verify.rq" <<'EOF'
SELECT ?s WHERE { ?s ?p ?o } ORDER BY ?s LIMIT 1
EOF
  cat > "$d/ggen.toml" <<'EOF'
[project]
name = "view2-aoq-c4"
version = "0.0.1"

[ontology]
source = "ontology/model.ttl"

[generation]
output_dir = "."

[[generation.rules]]
name = "aoq_c4_context"
mode = "Overwrite"
query = { file = "queries/c4_context.rq" }
template = { file = "templates/aoq_c4_context.mmd.tmpl" }
output_file = "docs/c4/aoq-c1-context.mmd"

[[generation.rules]]
name = "aoq_c4_containers"
mode = "Overwrite"
query = { file = "queries/c4_containers.rq" }
template = { file = "templates/aoq_c4_containers.mmd.tmpl" }
output_file = "docs/c4/aoq-c2-containers.mmd"

[[generation.rules]]
name = "verify_mermaid"
mode = "Overwrite"
query = { file = "queries/verify.rq" }
template = { file = "templates/verify_mermaid.mjs.tmpl" }
output_file = "scripts/verify-mermaid.mjs"
EOF
  ln -s "$NM" "$d/node_modules"
}

run_sync() { (cd "$1" && "$GGEN" sync run --skip-ea-admission) || { echo "FAIL ggen sync run in $1"; exit 1; }; }

A="$W/a"; setup "$A"; run_sync "$A"
C1="$A/docs/c4/aoq-c1-context.mmd"; C2="$A/docs/c4/aoq-c2-containers.mmd"
[ -s "$C1" ] && [ -s "$C2" ] || { echo "FAIL no mmd emitted"; exit 1; }

# verify_mermaid.mjs exits 0 on both
node /Users/sac/ggen/examples/archive/factory-paas/verify_mermaid.mjs "$C1" "$C2" || { echo "FAIL mermaid.parse"; exit 1; }

# every node label must appear verbatim in the aoq-pack ontology
for f in "$C1" "$C2"; do
  sed -n 's/^  [A-Za-z0-9_]*\["\(Person\|System\|Container\): \(.*\)"\]$/\2/p' "$f" | while IFS= read -r label; do
    grep -qF -- "$label" "$AOQ" || { echo "FAIL label not in aoq ttl: $label"; exit 1; }
  done || exit 1
done
n=$(grep -c '\["' "$C1" "$C2" | awk -F: '{s+=$2} END{print s}')
[ "$n" -ge 4 ] || { echo "FAIL too few nodes: $n"; exit 1; }

# staleness: rename one container subject label in a scratch copy, expect .mmd to change
B="$W/b"; setup "$B"
sed -i.bak 's/rdfs:label "AOQ frame"/rdfs:label "AOQ frame renamed"/' "$B/ontology/model.ttl"
grep -q 'AOQ frame renamed' "$B/ontology/model.ttl" || { echo "FAIL rename did not apply"; exit 1; }
run_sync "$B"
if diff -q "$C2" "$B/docs/c4/aoq-c2-containers.mmd" >/dev/null; then
  echo "FAIL container .mmd unchanged after rename (stale)"; exit 1
fi

# hand-edit does not survive re-sync
echo '  HAND["Container: hand"]' >> "$A/docs/c4/aoq-c2-containers.mmd"
run_sync "$A"
grep -q 'HAND' "$A/docs/c4/aoq-c2-containers.mmd" && { echo "FAIL hand edit survived re-sync"; exit 1; }

echo "VIEW2 OK"
