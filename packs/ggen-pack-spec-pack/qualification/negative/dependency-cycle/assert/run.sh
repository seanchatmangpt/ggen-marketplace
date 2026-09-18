#!/usr/bin/env bash
# T03 invalid corpus — refusal assertion: dependency-cycle
# Law: RFC-GPACK-001 v26.9.17 §34 — the dependency resolution result is a
# DAG; projection/semantic cycles are refused by default:
# REFUSED:DEPENDENCY_CYCLE. The fixture ships two packs (pack-a requires
# pack-b, pack-b requires pack-a); {{PACK}} is the entry pack pack-a, and
# the engine is expected to resolve pack-b from the same fixture root
# (env: PACK_A_DIR, PACK_B_DIR; see ../../README.md).
#
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURE_DIR="$(cd "$HERE/.." && pwd)"
CORPUS_DIR="$(cd "$FIXTURE_DIR/.." && pwd)"
# Entry subject is pack-a; the engine resolves pack-b from the same fixture
# root (map the two names to these paths in consumer config; see README).
PACK_DIR="$FIXTURE_DIR/pack-a"
PACK_A_DIR="$FIXTURE_DIR/pack-a"
PACK_B_DIR="$FIXTURE_DIR/pack-b"
export PACK_DIR FIXTURE_DIR CORPUS_DIR PACK_A_DIR PACK_B_DIR

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
