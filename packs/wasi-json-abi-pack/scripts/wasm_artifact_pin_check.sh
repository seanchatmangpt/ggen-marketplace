#!/bin/sh
# Gate: wasm_artifact_pin_check.sh — sha256+size artifact pin verification.
#
# Consolidates:
#   affidavit/affidavit-wasm/registry/ARTIFACTS.sha256 pin format
#     ("<kind> <sha256> <bytes> <name>", create-only)
#   affidavit/affidavit-wasm/tests/registry_artifacts.rs
#     (pin vs built-module sha256 + byte-length check; AFFIDAVIT_REQUIRE_PIN
#      turns "artifact absent" from a skip into a hard failure)
#   affidavit/.github/workflows/affidavit-wasm.yml "Checksum (must equal the
#     pin)" step.
#
# LAW GUARDED (wasi-json-abi-pack, gates/090_artifact_pin_shape.rq): a shipped
# wasm artifact is admitted only against a receipted pin — digest AND byte
# size AND pinned filename. The pin file is CREATE-ONLY: this gate verifies,
# it never writes a pin. Placeholder pins (digest not 64 lowercase hex) are
# never accepted as a match.
#
# Usage:
#   wasm_artifact_pin_check.sh --artifact FILE.wasm --pin PINFILE [--kind wasm]
#                              [--name BASENAME]
#     --artifact  the .wasm to verify
#     --pin       pin file; '#' lines are comments; data lines
#                 "<kind> <sha256> <bytes> <name>"
#     --kind      which pin line to admit (default: wasm)
#     --name      require the pin line to name this basename (default: derive
#                 from --artifact basename)
#
# Enforcement (mirrors AFFIDAVIT_REQUIRE_PIN semantics):
#   WASM_ARTIFACT_PIN_REQUIRE=1 makes absence loud:
#     - artifact missing while enforcement set  -> exit 3 REFUSED (never skip)
#     - no real pin line while enforcement set  -> exit 3 REFUSED (never skip)
#   Without enforcement: missing artifact or no real pin line -> exit 0 with
#   an explicit SKIPPED line on stderr (pin not checked), mirroring the test's
#   skip path. A WRONG pin (present but mismatched) always fails, enforced or
#   not: exit 1.
#
# Exit codes: 0 = pin verified (or explicit skip without enforcement);
#             1 = pin mismatch (digest, size, or name);
#             2 = usage error;
#             3 = enforcement violation (missing artifact/pin under
#                 WASM_ARTIFACT_PIN_REQUIRE).
set -u

ARTIFACT=""
PINFILE=""
KIND="wasm"
WANT_NAME=""

usage() { sed -n '2,44p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --artifact) [ $# -ge 2 ] || usage; ARTIFACT="$2";  shift ;;
    --pin)      [ $# -ge 2 ] || usage; PINFILE="$2";   shift ;;
    --kind)     [ $# -ge 2 ] || usage; KIND="$2";      shift ;;
    --name)     [ $# -ge 2 ] || usage; WANT_NAME="$2"; shift ;;
    -h|--help)  usage ;;
    *) echo "wasm_artifact_pin_check: unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done
[ -n "$PINFILE" ] || { echo "wasm_artifact_pin_check: --pin required" >&2; exit 2; }
[ -f "$PINFILE" ] || { echo "wasm_artifact_pin_check: no such pin file: $PINFILE" >&2; exit 2; }

REQUIRE="${WASM_ARTIFACT_PIN_REQUIRE:-}"

# --- enforcement: artifact must exist when REQUIRE is set (never skip) ------
if [ ! -f "$ARTIFACT" ]; then
  if [ -n "$REQUIRE" ]; then
    echo "GATE wasm_artifact_pin_check: REFUSED(enforcement_set_artifact_missing): WASM_ARTIFACT_PIN_REQUIRE is set but artifact is unset/missing: pin not checked" >&2
    exit 3
  fi
  echo "GATE wasm_artifact_pin_check: SKIPPED: artifact unset/missing: artifact pin not checked" >&2
  exit 0
fi
[ -n "$WANT_NAME" ] || WANT_NAME=$(basename "$ARTIFACT")

# --- read the pin line (create-only file; never written here) ----------------
PIN=$(awk -v k="$KIND" '$1==k && $2 ~ /^[0-9a-f]{64}$/ && $3 ~ /^[0-9]+$/ {print $2" "$3" "$4}' "$PINFILE" | head -n 1)
if [ -z "$PIN" ]; then
  if [ -n "$REQUIRE" ]; then
    echo "GATE wasm_artifact_pin_check: REFUSED(enforcement_set_pin_missing): WASM_ARTIFACT_PIN_REQUIRE is set but $PINFILE holds no real '$KIND' pin" >&2
    exit 3
  fi
  echo "GATE wasm_artifact_pin_check: SKIPPED: $PINFILE holds no real '$KIND' pin: not checked" >&2
  exit 0
fi
PIN_SHA=$(printf '%s' "$PIN"  | cut -d' ' -f1)
PIN_BYTES=$(printf '%s' "$PIN" | cut -d' ' -f2)
PIN_NAME=$(printf '%s' "$PIN"  | cut -d' ' -f3)

# --- compute the artifact's digest + size ------------------------------------
case "$(uname -s)" in
  Darwin) SHA=$(shasum -a 256 "$ARTIFACT" | cut -d' ' -f1) ;;
  *)      SHA=$(sha256sum "$ARTIFACT"     | cut -d' ' -f1) ;;
esac
BYTES=$(wc -c < "$ARTIFACT" | tr -d ' ')

echo "GATE wasm_artifact_pin_check: artifact=$ARTIFACT"
echo "  pin:    $PIN_SHA $PIN_BYTES $PIN_NAME"
echo "  actual: $SHA $BYTES $WANT_NAME"

FAIL=""
[ "$SHA" = "$PIN_SHA" ]       || FAIL="digest_mismatch"
[ "$BYTES" = "$PIN_BYTES" ]   || FAIL="$FAIL size_mismatch"
[ "$WANT_NAME" = "$PIN_NAME" ] || FAIL="$FAIL name_mismatch"
if [ -n "$FAIL" ]; then
  for f in $FAIL; do echo "  VIOLATION $f"; done
  echo "GATE wasm_artifact_pin_check: REFUSED(artifact does not match pinned $KIND)"
  exit 1
fi
echo "GATE wasm_artifact_pin_check: PASS (artifact matches pinned $KIND)"
exit 0
