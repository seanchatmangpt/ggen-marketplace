#!/usr/bin/env bash
# courts/shim_court.sh — template shim courts for ash-a2a-app-pack (lane L32). AUTHORED, NOT RUN.
# For each templates/*.tmpl whose frontmatter `to:` ends .ex/.exs: mutate a template in a TEMP COPY
# of the pack (real pack never edited), `ggen sync run --skip-ea-admission` + `mix test` in a fresh
# fixture project; BEFORE must be green, AFTER (shimmed) must be red, restore sha256 byte-exact.
# Usage: courts/shim_court.sh [template-basename ...]      (default: all Elixir templates)
# Env: GGEN_BIN (default ggen)  MIX_BIN (default mix)  SHIM_EXAMPLE (default examples/helpdesk)
#      SHIM_KEEP=1 keeps temp dirs.   Exit: 0 all PASS | 1 any FAIL | 3 nothing ran (SKIP).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REAL_PACK="$(cd "$HERE/.." && pwd)"
GGEN_BIN="${GGEN_BIN:-ggen}"; MIX_BIN="${MIX_BIN:-mix}"
EXAMPLE="${SHIM_EXAMPLE:-$REAL_PACK/examples/helpdesk}"
source "$HERE/lib.sh"
export GGEN_BIN MIX_BIN

repoint() { # repoint <ggen.toml> <pack-path>
    sed -i.bak -E "s#^(ash-a2a-app *= *\{ *path *= *\").*(\" *\})#\1$2\2#" "$1"; rm -f "$1.bak"
}

# ---- witness mode: fresh fixture from a pack copy; run sync (+ mix test) --------------------------
if [ "${1:-}" = "--witness" ]; then
    mode="$2"; pack="$3"; base="$4"
    fx="$(mktemp -d)"; trap '[ -n "${SHIM_KEEP:-}" ] || rm -r -f "$fx"' EXIT
    cp -R "$base/." "$fx/"
    repoint "$fx/ggen.toml" "$pack"
    cd "$fx"
    if ! "$GGEN_BIN" sync run --skip-ea-admission >/dev/null 2>&1; then
        echo "ggen sync failed ($mode)" >&2
        # a shim that breaks sync is a flip only if it is NOT the unmutated run
        [ "$mode" = after ] && exit 0 || exit 1
    fi
    marker() { grep -rIlq 'SHIM-COURT' --include='*.ex' --include='*.exs' --exclude-dir=deps --exclude-dir=_build .; }
    case "$mode" in
      before) "$MIX_BIN" test ;;
      probe)  marker ;;
      after)  marker || { echo "shim not materialized in generated output" >&2; exit 1; }
              if "$MIX_BIN" test; then echo "mix test stayed GREEN under shim" >&2; exit 1; fi ;;
    esac
    exit 0
fi

command -v "$GGEN_BIN" >/dev/null 2>&1 || shim_court_skip "ggen not found ($GGEN_BIN)"
command -v "$MIX_BIN"  >/dev/null 2>&1 || shim_court_skip "mix not found ($MIX_BIN)"
[ -f "$EXAMPLE/ggen.toml" ] || shim_court_skip "fixture example missing: $EXAMPLE"

WORK="$(mktemp -d)"; trap '[ -n "${SHIM_KEEP:-}" ] || rm -r -f "$WORK"' EXIT
tree_sha() { (cd "$REAL_PACK/templates" && find . -type f | sort | xargs shasum -a 256 | shasum -a 256 | awk '{print $1}'); }
REAL_SHA_BEFORE="$(tree_sha)"

PACK_SRC="$WORK/pack-src"; cp -R "$REAL_PACK" "$PACK_SRC"; rm -r -f "$PACK_SRC/courts"

# Self-check on a real template copy: a corrupted restore must be detected.
first_tmpl="$(ls "$PACK_SRC"/templates/*.tmpl | head -1)"
shim_court_self_check "$first_tmpl" || exit 1

# Base fixture: deps fetched + compiled once, reused by every witness via cp -R.
BASE="$WORK/base"; mkdir -p "$BASE"; cp -R "$EXAMPLE/." "$BASE/"
repoint "$BASE/ggen.toml" "$PACK_SRC"
( cd "$BASE" && "$GGEN_BIN" sync run --skip-ea-admission >/dev/null && "$MIX_BIN" deps.get >/dev/null \
    && "$MIX_BIN" compile >/dev/null ) \
    || shim_court_skip "base fixture does not sync+compile (environment: deps/network?); no court can run"

apply_shim() {
    # Insert a top-level raise right after the frontmatter's closing '---'. In a generated .exs it
    # raises at load; in a generated .ex it raises at compile: mix test goes red.
    awk 'BEGIN{n=0} {print} /^---[[:space:]]*$/ {n++; if(n==2) print "raise \"SHIM-COURT\"  # SHIM-COURT"}' \
        "$SHIM_FILE" > "$SHIM_FILE.new" && mv "$SHIM_FILE.new" "$SHIM_FILE"
}

targets=()
if [ "$#" -gt 0 ]; then targets=("$@"); else
    for t in "$PACK_SRC"/templates/*.tmpl; do
        if grep -Eq '^to:.*\.exs?"?[[:space:]]*$' "$t"; then targets+=("$(basename "$t")"); fi
    done
fi

pass=0; fail=0; skip=0
for tn in "${targets[@]}"; do
    SHIM_COURT_NAME="shim:$tn"
    P="$WORK/pack-$tn"; rm -r -f "$P"; cp -R "$PACK_SRC" "$P"
    # Probe (shim on a throwaway copy): does the fixture materialize this template at all?
    SHIM_FILE="$P/templates/$tn"; apply_shim
    if ! bash -uc "'$0' --witness probe '$P' '$BASE'" >/dev/null 2>&1; then
        printf '[SKIP] %s: fixture %s does not materialize this template\n' "$SHIM_COURT_NAME" "$EXAMPLE"
        skip=$((skip+1)); continue
    fi
    rm -r -f "$P"; cp -R "$PACK_SRC" "$P"
    if ( with_shim "$P/templates/$tn" \
            "'$0' --witness before '$P' '$BASE'" \
            "'$0' --witness after '$P' '$BASE'" ); then pass=$((pass+1)); else fail=$((fail+1)); fi
    rm -r -f "$P"
done

[ "$(tree_sha)" = "$REAL_SHA_BEFORE" ] || { echo "[FAIL:RESTORE] real pack templates changed" >&2; exit 1; }
printf '[summary] pass=%d fail=%d skip=%d (real pack templates sha256 unchanged)\n' "$pass" "$fail" "$skip"
[ "$fail" -eq 0 ] || exit 1
[ "$pass" -gt 0 ] || exit 3
