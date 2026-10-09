#!/usr/bin/env bash
# rollout.sh — doc-hdit fleet rollout runner (rust-doc-hdit-pack).
#
# For each fleet repo: extract code+doc surfaces (reusing a precomputed inputs
# JSON keyed by a content hash of the extractor script + repo HEAD SHA), run
# doc-hdit vectorize +
# certify against courts/doc_quality.court. PASS mints a chained receipt;
# FAIL records {repo, gate, value, top offending claims} to a failure ledger
# and the loop continues. Summary table at end; nonzero exit if any FAIL
# (suppress with --report-only).
#
# Usage:
#   rollout.sh [--report-only] [--court FILE] [--out DIR] [--work DIR] [REPO_DIR...]
#
# Env:
#   DOC_HDIT_BIN  doc-hdit binary (default: resolved from PATH)
#
# Exit: 0 all repos PASS (or --report-only); 1 any FAIL; 2 usage/environment error.

set -euo pipefail

usage() { sed -n '2,14p' "$0"; exit 2; }

REPORT_ONLY=0
COURT=""
OUT=""
WORK=""
REPOS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --report-only) REPORT_ONLY=1; shift ;;
    --court) COURT="${2:?--court requires a value}"; shift 2 ;;
    --out) OUT="${2:?--out requires a value}"; shift 2 ;;
    --work) WORK="${2:?--work requires a value}"; shift 2 ;;
    -h|--help) usage ;;
    -*) echo "rollout.sh: unknown option: $1" >&2; exit 2 ;;
    *) REPOS+=("$1"); shift ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COURT="${COURT:-$PACK_DIR/courts/doc_quality.court}"
OUT="${OUT:-/tmp/hdit/rollout}"
WORK="${WORK:-$OUT/work}"
HDIT_CACHE="${HDIT_CACHE:-/tmp/hdit}"

DOC_HDIT_BIN="${DOC_HDIT_BIN:-$(command -v doc-hdit || true)}"
[ -n "$DOC_HDIT_BIN" ] || { echo "rollout.sh: doc-hdit not found on PATH (set DOC_HDIT_BIN)" >&2; exit 2; }
[ -f "$COURT" ] || { echo "rollout.sh: court file not found: $COURT" >&2; exit 2; }

if [ ${#REPOS[@]} -eq 0 ]; then
  # Fleet map: the 20 doc-hdit pilot repos at /Users/sac.
  FLEET="affidavit ash_a2a ash_affidavit ash_ex4pm ash_graphlaw ash_pplan \
ash_r2rml ash_surface autofde-lab beam4pm castle ex4pm ferroplan \
frozen-duckdb ggen-marketplace graphlaw gymact wasm4pm xaas zcode-cli"
  for name in $FLEET; do
    if [ -d "/Users/sac/$name" ]; then REPOS+=("/Users/sac/$name");
    else echo "rollout.sh: fleet repo missing: /Users/sac/$name" >&2; exit 2; fi
  done
fi

mkdir -p "$OUT" "$WORK" "$OUT/receipts" "$HDIT_CACHE"
LEDGER="$OUT/failures.jsonl"
: > "$LEDGER"
SUMMARY="$OUT/summary.txt"
: > "$SUMMARY"

GEN="$PACK_DIR/../../scripts/gen_doc_surface.py"
GEN="$(cd "$(dirname "$GEN")" && pwd)/$(basename "$GEN")"

# build_inputs <repo_dir> <name> — emit the combined inputs JSON path on stdout.
# Cache key is a content hash (sha256 of the extractor script bytes+mtime and
# the repo's HEAD SHA), not a cache-file mtime comparison: any extractor change
# (edit or touch, e.g. new surface arrays) or repo head move forces a cache
# miss, so stale pre-[51] inputs can never be replayed.
build_inputs() {
  repo="$1" name="$2"
  gen_hash="$( { shasum -a 256 "$GEN"; stat -f %m "$GEN"; } | shasum -a 256 | awk '{print $1}')"
  head_sha="$(git -C "$repo" rev-parse HEAD 2>/dev/null || echo no-vcs)"
  cache_key="$(printf '%s\n%s' "$gen_hash" "$head_sha" | shasum -a 256 | awk '{print $1}')"
  cache_file="$HDIT_CACHE/$name.$cache_key.inputs.json"
  if [ -f "$cache_file" ]; then
    printf '%s\n' "$cache_file"
    return 0
  fi
  inputs="$cache_file"
  python3 "$GEN" code "$repo" > "$WORK/$name.code.json"
  python3 "$GEN" doc "$repo" --code-json "$WORK/$name.code.json" > "$WORK/$name.doc.json"
  python3 - "$WORK/$name.code.json" "$WORK/$name.doc.json" "$inputs" <<'PY'
import json, sys
code = json.load(open(sys.argv[1]))
doc = json.load(open(sys.argv[2]))
# Carry the code surface through the merge: `directories` grounds
# trailing-slash doc references (exact membership), `paths` grounds
# path_ref claims (P1 [47]), and `known_external` grounds
# external_documented claims (P1 [80]; a dropped array scores every
# external_documented claim as a phantom). `.get` keeps pre-[47]
# extractors working (backward-compatible optional fields).
json.dump({"modules": code.get("modules", []),
           "claims": doc.get("claims", []),
           "directories": code.get("directories", []),
           "paths": code.get("paths", []),
           "known_external": code.get("known_external", [])},
          open(sys.argv[3], "w"), indent=2, sort_keys=True)
PY
  printf '%s\n' "$inputs"
}

# top_claims <vec.json> <n> — space-separated "subject::object" of the worst
# ungrounded claims (phantom_ranking entries with grounded == false).
top_claims() {
  python3 - "$1" "${2:-3}" <<'PY'
import json, sys
try:
    data = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
ranked = data.get("phantom_ranking") or []
n = int(sys.argv[2])
out = []
for entry in ranked:
    if entry.get("grounded"):
        continue
    idx = entry.get("claim_index")
    claim = (data.get("_claims") or {}).get(str(idx)) or {}
    out.append("%s:%s::%s" % (idx, claim.get("subject", "?"), claim.get("object", "?")))
    if len(out) >= n:
        break
print("|".join(out) if out else "-")
PY
}

PASS_COUNT=0
FAIL_COUNT=0

printf '%-20s %-6s %-10s %s\n' "REPO" "RESULT" "GATE" "RECEIPT/LEDGER" >> "$SUMMARY"

for repo in "${REPOS[@]}"; do
  repo="$(cd "$repo" && pwd)"
  name="$(basename "$repo")"
  echo "== $name =="
  if ! inputs="$(build_inputs "$repo" "$name")"; then
    echo "  ERROR: surface extraction failed" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1))
    printf '{"repo":"%s","gate":"extraction","value":"error"}\n' "$name" >> "$LEDGER"
    printf '%-20s %-6s %-10s %s\n' "$name" "ERROR" "extraction" "-" >> "$SUMMARY"
    continue
  fi

  vec="$WORK/$name.vec.json"
  if ! "$DOC_HDIT_BIN" vectorize "$inputs" > "$vec" 2>"$WORK/$name.vectorize.err"; then
    echo "  ERROR: vectorize failed" >&2
    FAIL_COUNT=$((FAIL_COUNT + 1))
    printf '{"repo":"%s","gate":"vectorize","value":"error"}\n' "$name" >> "$LEDGER"
    printf '%-20s %-6s %-10s %s\n' "$name" "ERROR" "vectorize" "-" >> "$SUMMARY"
    continue
  fi

  chain="$OUT/receipts/$name.receipts.jsonl"
  claims_idx="$WORK/$name.claims.json"
  python3 - "$inputs" "$claims_idx" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
json.dump({str(i): c for i, c in enumerate(d.get("claims", []))}, open(sys.argv[2], "w"))
PY
  python3 - "$vec" "$claims_idx" "$vec" <<'PY'
import json, sys
vec_path, claims_path = sys.argv[1], sys.argv[2]
data = json.load(open(vec_path))
data["_claims"] = json.load(open(claims_path))
json.dump(data, open(vec_path, "w"), indent=1, sort_keys=True)
PY
  claims="$WORK/$name.claims.json"
  worst="$(top_claims "$vec" 3)"

  set +e
  "$DOC_HDIT_BIN" certify "$inputs" "$COURT" --chain "$chain" \
    > "$WORK/$name.certify.out" 2> "$WORK/$name.certify.err"
  cert_rc=$?
  set -e

  if [ "$cert_rc" -eq 0 ]; then
    PASS_COUNT=$((PASS_COUNT + 1))
    echo "  PASS — receipt: $chain"
    printf '%-20s %-6s %-10s %s\n' "$name" "PASS" "-" "$chain" >> "$SUMMARY"
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
    gate_line="$(grep -m1 'REFUSED:DOC_HDIT_CERTIFY_GATE_FAIL' "$WORK/$name.certify.err" || true)"
    gate="$(printf '%s' "$gate_line" | sed -E 's/.*GATE_FAIL:([^ ]+) value=.*/\1/')"
    value="$(printf '%s' "$gate_line" | sed -E 's/.*value=([0-9.eE+-]+).*/\1/')"
    [ -n "$gate" ] || gate="unknown"
    [ -n "$value" ] || value="n/a"
    python3 - "$LEDGER" "$name" "$gate" "$value" "$worst" <<'PY'
import json, sys
path, repo, gate, value, worst = sys.argv[1:6]
claims = [] if worst == "-" else [
    {"claim_index": int(t.split(":", 1)[0]), "subject": t.split("::")[0].split(":", 1)[1],
     "object": t.split("::", 1)[1]}
    for t in worst.split("|")
]
json.dump({"repo": repo, "gate": gate, "value": value, "top_offending_claims": claims},
          open(path, "a"), sort_keys=True)
open(path, "a").write("\n")
PY
    echo "  FAIL — $gate ($value); top claims: $worst"
    printf '%-20s %-6s %-10s %s\n' "$name" "FAIL" "$gate" "$LEDGER" >> "$SUMMARY"
  fi
done

echo
echo "=== doc-hdit rollout summary ($OUT) ==="
cat "$SUMMARY"
echo
echo "PASS: $PASS_COUNT  FAIL/ERROR: $FAIL_COUNT"
[ "$FAIL_COUNT" -eq 0 ] || echo "Failure ledger: $LEDGER"

if [ "$FAIL_COUNT" -gt 0 ] && [ "$REPORT_ONLY" -ne 1 ]; then
  exit 1
fi
exit 0
