#!/usr/bin/env bash
# T03 invalid corpus — refusal assertion: symlink
# Law: RFC-GPACK-001 v26.9.17 §72 — the strict portable source profile
# refuses symlinks inside pack source: REFUSED:PACK_SYMLINK.
#
# THIS FIXTURE'S RUN.SH WORKS ON A SCRATCH COPY: it copies the pack to a
# temp dir, materializes the symlinked source file there via setup.sh, and
# points the engine at the copy. The git tree never contains a symlink
# (ticket acceptance #3; repo law: no symlinks under packs/).
#
# Contract (see ../../README.md "How to assert") is otherwise identical to
# the other fixtures: engines print typed refusals on stderr; stdout AND
# stderr are captured; exit 0 IFF the exact typed code from
# assert/refusal-code.txt appears; bare crash text never passes (§15/§83).
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURE_DIR="$(cd "$HERE/.." && pwd)"
CORPUS_DIR="$(cd "$FIXTURE_DIR/.." && pwd)"
export FIXTURE_DIR CORPUS_DIR

if [ "$#" -lt 1 ]; then
  echo "usage: run.sh <engine-command-template containing {{PACK}}>" >&2
  exit 2
fi
TEMPLATE="$1"
case "$TEMPLATE" in
*"{{PACK}}"*) ;;
*)
  echo "REFUSED:ASSERT_TEMPLATE_INVALID: engine command template must contain {{PACK}}" >&2
  exit 2
  ;;
esac
EXPECTED="$(grep -v '^[[:space:]]*#' "$HERE/refusal-code.txt" | head -n 1 | tr -d '[:space:]')"
if [ -z "$EXPECTED" ]; then
  echo "REFUSED:ASSERT_EXPECTED_CODE_EMPTY: assert/refusal-code.txt carries no expected code" >&2
  exit 2
fi

# Materialize the attack on a scratch copy so the checked-in tree stays
# symlink-free (marketplace.py refuses any symlink under packs/).
SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/gpack-t03-symlink.XXXXXX")"
PACK_DIR="$SCRATCH/pack"
cleanup() { rm -rf "$SCRATCH"; }
trap cleanup EXIT
mkdir -p "$PACK_DIR"
(cd "$FIXTURE_DIR" && tar cf - --exclude assert --exclude setup.sh .) | (cd "$PACK_DIR" && tar xf -)
bash "$FIXTURE_DIR/setup.sh" "$PACK_DIR" >&2
export PACK_DIR

COMMAND="${TEMPLATE//\{\{PACK\}\}/$PACK_DIR}"
OUTPUT="$(bash -c "$COMMAND" 2>&1)"
STATUS="$?"
printf '%s\n' "$OUTPUT"

if printf '%s\n' "$OUTPUT" | grep -Fq "$EXPECTED"; then
  echo "OBSERVED $EXPECTED (engine exit=$STATUS)"
  exit 0
fi
if printf '%s\n' "$OUTPUT" | grep -Eq 'panicked at|RUST_BACKTRACE|Segmentation fault|core dumped|Traceback \(most recent call last\)'; then
  echo "FAILED: bare crash text without typed refusal $EXPECTED — a crash is not a refusal (RFC §15, §83)" >&2
  exit 1
fi
if [ "$STATUS" -eq 0 ] && [ -z "$OUTPUT" ]; then
  echo "FAILED: silent null engine emitted no refusal — assertion refuses to pass vacuously (RFC §77)" >&2
  exit 1
fi
echo "FAILED: expected typed refusal $EXPECTED not present in engine output (engine exit=$STATUS)" >&2
exit 1
