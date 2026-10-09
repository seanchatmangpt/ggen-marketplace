#!/bin/sh
# install-pin-hook.sh -- install the R62/R81 commit-hook pin-freshness guard.
#
# Installs two hooks into $GIT_DIR/hooks (default .git/hooks):
#
#   pre-commit : if the staged diff touches scripts/gen_doc_surface.py,
#                write $GIT_DIR/PIN-CHECK-PENDING and exit 0 with a loud
#                warning. The pre-commit stage cannot see this commit's own
#                ledger update, so verification is DEFERRED, not skipped.
#   post-commit: if PIN-CHECK-PENDING exists, verify that
#                `git show HEAD:docs/sjira/v26.10.8/PIN-ROTATION-LEDGER.md`
#                contains the sha256 of the COMMITTED extractor bytes
#                (`git show HEAD:scripts/gen_doc_surface.py`, hashed from an
#                archived temp copy). Pass -> remove the marker. Fail -> LOUD
#                error (commit landed but pin law violated; repair: immediate
#                follow-up commit), exit 1, keep the marker.
#
# Idempotent: existing hook files are preserved; this guard is appended as a
# marker-delimited block and re-installing replaces only that block. The
# git-lfs post-commit hook is NOT clobbered. Never touches
# scripts/gen_doc_surface.py.
set -eu

GIT_DIR="$(git rev-parse --absolute-git-dir)"
HOOKS="$GIT_DIR/hooks"
MARKER="$GIT_DIR/PIN-CHECK-PENDING"
mkdir -p "$HOOKS"

PRE="$HOOKS/pre-commit"
POST="$HOOKS/post-commit"

BEGIN='# >>> pin-freshness-guard (R81) >>>'
END='# <<< pin-freshness-guard (R81) <<<'

append_block() {
  _file="$1"
  _block="$2"
  [ -f "$_file" ] || printf '#!/bin/sh\n' > "$_file"
  chmod +x "$_file"
  sed -e "/$BEGIN/,/$END/d" "$_file" > "$_file.tmp"
  cat "$_file.tmp" > "$_file"   # rewrite in place, preserves mode
  rm -f "$_file.tmp"
  printf '\n%s\n%s\n%s\n' "$BEGIN" "$_block" "$END" >> "$_file"
}

PRE_BODY='
if git diff --cached --name-only | grep -q "^scripts/gen_doc_surface\.py$"; then
  printf "%s\n" "PIN-CHECK-PENDING" > "'"$MARKER"'"
  echo "=============================================================" >&2
  echo "PIN-FRESHNESS: extractor change staged." >&2
  echo "  Pre-commit CANNOT verify this commit'"'"'s own ledger row." >&2
  echo "  Verification DEFERRED to post-commit (marker written)." >&2
  echo "  This commit MUST pair scripts/gen_doc_surface.py with a" >&2
  echo "  PIN-ROTATION-LEDGER.md current-row update." >&2
  echo "=============================================================" >&2
fi
exit 0
'

POST_BODY='
if [ -f "'"$MARKER"'" ]; then
  TMP_HASH="$(mktemp)"
  TMP_LEDGER="$(mktemp)"
  if git show HEAD:scripts/gen_doc_surface.py > "$TMP_HASH" 2>/dev/null; then
    EXTRACT_HASH="$(shasum -a 256 "$TMP_HASH" | awk '"'"'{print $1}'"'"')"
    if git show HEAD:docs/sjira/v26.10.8/PIN-ROTATION-LEDGER.md > "$TMP_LEDGER" 2>/dev/null \
       && grep -i "current" "$TMP_LEDGER" | grep -q "$EXTRACT_HASH"; then
      echo "pin-freshness: OK committed extractor sha256 $EXTRACT_HASH found in ledger current row."
      rm -f "'"$MARKER"'"
    else
      cat >&2 <<R81FAIL
*************************************************************
* PIN LAW VIOLATED (R62/R81)                                *
* Commit $(git rev-parse --short HEAD) landed WITHOUT a     *
* matching PIN-ROTATION-LEDGER.md current-row hash for the  *
* committed extractor (sha256 $EXTRACT_HASH).               *
* REPAIR: immediately commit the ledger current-row update  *
* as a follow-up commit. Marker kept until repaired.        *
*************************************************************
R81FAIL
    fi
  else
    echo "pin-freshness: cannot read committed extractor at HEAD; marker kept." >&2
  fi
  rm -f "$TMP_HASH" "$TMP_LEDGER"
  # post-commit cannot roll back; exit 1 only makes the violation VISIBLE.
  [ -f "'"$MARKER"'" ] && exit 1
fi
exit 0
'

append_block "$PRE" "$PRE_BODY"
append_block "$POST" "$POST_BODY"

echo "install-pin-hook: installed pin-freshness guard in:"
echo "  $PRE"
echo "  $POST"
echo "  marker path: $MARKER"
