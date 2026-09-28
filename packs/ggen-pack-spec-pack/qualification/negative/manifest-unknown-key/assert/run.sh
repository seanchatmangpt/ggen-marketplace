#!/usr/bin/env bash
# T03 invalid corpus — refusal assertion: manifest-unknown-key
# Law: RFC-GPACK-001 v26.9.17 §7.1 — a Core v1 implementation MUST reject
# unknown keys inside [pack]. Expected typed refusal: REFUSED:PACK_MANIFEST_INVALID.
#
# Contract (see ../../README.md "How to assert"):
#   assert/run.sh "<engine-command-template>"
#   * The template is a shell command string containing the literal
#     placeholder {{PACK}}; run.sh replaces it with the absolute path of the
#     attack pack handed to the engine (here: this fixture directory).
#   * The template runs with env: PACK_DIR, FIXTURE_DIR, CORPUS_DIR.
#   * Engines print typed refusals on stderr; run.sh captures stdout AND
#     stderr and exits 0 IFF the combined output contains the exact typed
#     code from assert/refusal-code.txt.
#   * Bare crash text (panic/backtrace/traceback) is NOT a refusal (§15/§83):
#     without the typed code this script always exits non-zero, so it cannot
#     pass vacuously against a silent/null engine (§77).
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURE_DIR="$(cd "$HERE/.." && pwd)"
CORPUS_DIR="$(cd "$FIXTURE_DIR/.." && pwd)"
PACK_DIR="$FIXTURE_DIR"
export PACK_DIR FIXTURE_DIR CORPUS_DIR

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
