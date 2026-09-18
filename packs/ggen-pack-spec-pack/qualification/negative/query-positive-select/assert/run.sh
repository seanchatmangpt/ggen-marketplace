#!/usr/bin/env bash
# T03 invalid corpus — POSITIVE assertion: query-positive-select
# Law: RFC-GPACK-001 v26.9.17 §96 row 1 — "Put a returning SELECT in
# queries/; rows must not refuse." This fixture is the non-attacking half of
# the D1 falsifier pair (§4.4 divergence D1; §5.6 Query is not Gate; §13):
# its queries/d1_select.rq is byte-identical to the refusing gate in
# ../gate-positive-select/gates/010_positive_select.rq — only the surface
# differs. An engine that refuses here has collapsed Query into Gate.
#
# Expected outcome (assert/refusal-code.txt): NO_REFUSAL:QUERY_ROWS_MUST_RENDER
#   * the engine completes (exit 0),
#   * emits NO `REFUSED:` token on any stream,
#   * AND emits the query row value (the pack IRI bound to ?s) — a silent
#     null engine must NOT pass: the assertion requires positive evidence
#     that the rows were processed (§77: RequiredOutcomeObserved).
#
# Contract (see ../../README.md "How to assert"):
#   assert/run.sh "<engine-command-template containing {{PACK}}>"
#   Engines print typed refusals on stderr; stdout AND stderr are captured.
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
  echo "REFUSED:ASSERT_EXPECTED_CODE_EMPTY: assert/refusal-code.txt carries no expected outcome" >&2
  exit 2
fi
case "$EXPECTED" in
NO_REFUSAL:*) ;;
*)
  echo "REFUSED:ASSERT_EXPECTED_OUTCOME_INVALID: this fixture asserts a non-refusal; expected outcome must be NO_REFUSAL:*" >&2
  exit 2
  ;;
esac

COMMAND="${TEMPLATE//\{\{PACK\}\}/$PACK_DIR}"
OUTPUT="$(bash -c "$COMMAND" 2>&1)"
STATUS="$?"
printf '%s\n' "$OUTPUT"

fail() {
  echo "FAILED: $1" >&2
  exit 1
}

if [ "$STATUS" -ne 0 ]; then
  fail "engine exited $STATUS — the query surface must complete without refusing (§13, §96 row 1)"
fi
if printf '%s\n' "$OUTPUT" | grep -Fq 'REFUSED:'; then
  fail "engine emitted a REFUSED token for a queries/ SELECT — Gate/Query conflation (D1, §5.6, §96 row 1)"
fi
MARKER="urn:ggen:pack:mkt03-query-positive-select"
if printf '%s\n' "$OUTPUT" | grep -Fq "$MARKER"; then
  echo "OBSERVED query rows without refusal (D1 positive half, §96 row 1; row value $MARKER)"
  exit 0
fi
if [ -z "$OUTPUT" ]; then
  fail "silent null engine: no rows observed — assertion refuses to pass vacuously (§77 RequiredOutcomeObserved)"
fi
fail "expected query row value $MARKER not present in engine output (positive evidence required by §77)"
