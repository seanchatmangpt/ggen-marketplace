#!/usr/bin/env bash
# T03 invalid corpus — acceptance falsifier #1 (ticket): no assertion in this
# corpus may pass vacuously. Runs every assert/run.sh against the null
# engine (null-engine.sh: silent, exit 0) and exits 0 IFF ALL fixtures
# correctly FAIL (exit non-zero). Any VACUOUS-PASS line is a broken
# assertion and fails the run.
#
# Usage: run-null-falsifier.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NULL_STUB="$HERE/null-engine.sh"

total=0
vacuous=0
for run in "$HERE"/*/assert/run.sh; do
  name="$(basename "$(dirname "$(dirname "$run")")")"
  total=$((total + 1))
  if bash "$run" "$NULL_STUB {{PACK}}" >/dev/null 2>&1; then
    echo "VACUOUS-PASS (BAD): $name exited 0 against the null engine"
    vacuous=$((vacuous + 1))
  else
    rc=$?
    echo "correctly-refused-null (exit=$rc): $name"
  fi
done

echo "null-engine falsifier: $((total - vacuous))/$total fixtures correctly fail against the null engine"
if [ "$vacuous" -ne 0 ]; then
  echo "FAILED: $vacuous assertion(s) can pass vacuously — they are not falsifiers (§77)" >&2
  exit 1
fi
echo "OK: no assertion in this corpus passes vacuously"
exit 0
