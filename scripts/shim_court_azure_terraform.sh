#!/usr/bin/env bash
# Shim court: azure-terraform-pack (runs `ggen sync run --skip-ea-admission` +
# `terraform fmt -check` / `init` / `validate` / `test` inside a temp copy).
# Never mutates tracked templates in place.
# Missing `terraform` binary -> exit 3 ([SKIP]); broken templates/ontology/sync -> exit 1 (FAIL).
# Self-check (--self-check): corrupts a restore on a temp copy; must exit 1.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PACK_DIR="$ROOT/packs/azure-terraform-pack"
sha() { shasum -a 256 "$1" | awk '{print $1}'; }

if ! command -v terraform >/dev/null 2>&1; then
  echo "[SKIP] terraform binary unavailable"
  exit 3
fi

if ! command -v ggen >/dev/null 2>&1; then
  echo "[FAIL] ggen binary unavailable"
  exit 1
fi

check() { # $1 = temp pack dir ; rc 0 = sync + fmt + validate + test pass
  local pack="$1"
  cat > "$pack/ggen.toml" <<'TOML'
[project]
name = "azure-tf-shim-court"

[ontology]
source = "ontology.ttl"

[templates]
dir = "templates"
TOML
  rm -rf "$pack/deploy"
  if ! (cd "$pack" && ggen sync run --skip-ea-admission >"$pack/.sync.log" 2>&1); then
    echo "ggen sync run failed:"
    tail -20 "$pack/.sync.log" 2>/dev/null || true
    return 1
  fi
  local tf_dir="$pack/deploy/azure/crown-bribery-case"
  if [ ! -d "$tf_dir" ]; then
    echo "expected generated dir missing: $tf_dir"
    return 1
  fi
  if ! terraform fmt -check -recursive "$pack/deploy/azure" >"$pack/.fmt.log" 2>&1; then
    echo "terraform fmt -check failed:"
    cat "$pack/.fmt.log"
    return 1
  fi
  local rc=0
  (
    cd "$tf_dir" &&
    terraform init -backend=false -input=false -no-color >"$pack/.tf.log" 2>&1 &&
    terraform validate -no-color >>"$pack/.tf.log" 2>&1 &&
    terraform test -no-color >>"$pack/.tf.log" 2>&1
  ) || rc=$?
  tail -10 "$pack/.tf.log" 2>/dev/null || true
  if [ -n "${CHECK_OUT:-}" ]; then
    cp "$pack/.tf.log" "$CHECK_OUT" 2>/dev/null || true
  fi
  return "$rc"
}

court() {
  local work; work="$(mktemp -d)"
  cp -R "$PACK_DIR/." "$work/"
  local f="$work/templates/main.tf.tmpl"
  local base; base="$(sha "$f")"
  echo "BASELINE sha256=$base"

  check "$work"; local b=$?; echo "BEFORE rc=$b"
  if [ "$b" -ne 0 ]; then
    echo "FAIL: baseline check not green (broken template, ontology, or terraform check)"
    rm -rf "$work"
    return 1
  fi

  cp "$f" "$f.court-orig"
  sed 's/restart_policy      = "{{ group.restartPolicy }}"/restart_policy      = "Always" # SHIM-COURT/' "$f.court-orig" > "$f"
  echo "SHIM applied sha256=$(sha "$f")"

  local ao; ao="$(mktemp)"; CHECK_OUT="$ao" check "$work"; local a=$?; echo "AFTER rc=$a"
  grep -q "restart_policy" "$ao" || a=0
  rm -f "$ao"

  cp "$f.court-orig" "$f"
  [ "${CORRUPT_RESTORE:-0}" = 1 ] && echo "# corrupt" >> "$f"
  rm -f "$f.court-orig"

  local after; after="$(sha "$f")"
  if [ "$after" = "$base" ]; then
    echo "RESTORE sha256=$after MATCH"
  else
    echo "RESTORE sha256=$after MISMATCH"
    rm -rf "$work"
    return 1
  fi

  rm -rf "$work"
  if [ "$a" -eq 0 ]; then
    echo "VACUOUS GATE: shim did not flip the restart_policy assertion"
    return 1
  fi
  echo "COURT PASS"
}

if [ "${1:-}" = "--self-check" ]; then
  CORRUPT_RESTORE=1 court; rc=$?
  [ "$rc" -eq 1 ] && { echo "SELF-CHECK PASS (corrupt restore detected)"; exit 0; }
  echo "SELF-CHECK FAIL rc=$rc"; exit 1
fi

court; exit $?
