#!/usr/bin/env bash
# T03 invalid corpus — refusal assertion: ambiguous-capability
# Law: RFC-GPACK-001 v26.9.17 §31 — capability resolution MUST be
# deterministic; with multiple incompatible providers and no selection rule:
# REFUSED:AMBIGUOUS_CAPABILITY_PROVIDER. The fixture ships a consumer pack
# plus two provider packs of the same capability; {{PACK}} is the consumer.
#
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURE_DIR="$(cd "$HERE/.." && pwd)"
CORPUS_DIR="$(cd "$FIXTURE_DIR/.." && pwd)"
# Entry subject is the consumer pack; the engine resolves both provider packs
# from the same fixture root (map the names to these paths; see README).
PACK_DIR="$FIXTURE_DIR/consumer"
CONSUMER_DIR="$FIXTURE_DIR/consumer"
PROVIDER_ALPHA_DIR="$FIXTURE_DIR/provider-alpha"
PROVIDER_BETA_DIR="$FIXTURE_DIR/provider-beta"
export PACK_DIR FIXTURE_DIR CORPUS_DIR CONSUMER_DIR PROVIDER_ALPHA_DIR PROVIDER_BETA_DIR

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
