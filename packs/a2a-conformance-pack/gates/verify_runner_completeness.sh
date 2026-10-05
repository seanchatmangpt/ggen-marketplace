#!/usr/bin/env bash
# runner-completeness gate -- EXECUTABLE half (the SPARQL half is
# 020_runner_completeness.rq over the pack graph).
#
# Falsifier: "the runner task exists and its court list matches the pack's
# inventory." This script executes that falsifier against the REAL runner
# source and the REAL filesystem:
#   1. the runner task source file must exist;
#   2. every path on the runner's @v1_courts list must exist on disk;
#   3. the runner's list and the pack's ontology inventory (a2ac:CourtFile
#      a2ac:courtFile rows) must be THE SAME SET, order included.
set -euo pipefail

REPO="${1:-/Users/sac/ash_a2a}"
PACK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ONTOLOGY="$PACK_DIR/ontology.ttl"

fail() { echo "RUNNER-COMPLETENESS FAIL: $*" >&2; exit 1; }

RUNNER="$REPO/lib/mix/tasks/ash_a2a.v1_conformance_report.ex"
[ -f "$RUNNER" ] || fail "runner task source not found at $RUNNER (falsifier leg 1: the runner task exists)"

# The runner's maintained @v1_courts list, parsed from the real source in
# declaration order.
RUNNER_LIST="$(sed -n '/@v1_courts \[/,/\]/p' "$RUNNER" | grep -o '"test/ash_a2a_v1_[^"]*"' | tr -d '"')"
[ -n "$RUNNER_LIST" ] || fail "could not parse @v1_courts from $RUNNER"

# Leg 2: every listed court exists on disk (a court you cannot execute is
# not a court that passed -- the runner itself enforces this at runtime too).
while IFS= read -r court; do
  [ -f "$REPO/$court" ] || fail "court file listed by the runner is missing on disk: $court"
done <<< "$RUNNER_LIST"

# The pack's inventory: every a2ac:CourtFile a2ac:courtFile row in ontology.ttl,
# in runnerListIndex order (the index is part of the row, so sort by it).
PACK_LIST="$(python3 - "$ONTOLOGY" <<'PY'
import re, sys
ttl = open(sys.argv[1]).read()
rows = re.findall(r'a2ac:runnerListIndex (\d+)\s*;\s*\n\s*a2ac:courtFile "([^"]+)"', ttl)
if not rows:
    sys.exit("FAIL: no a2ac:CourtFile inventory rows found in ontology.ttl")
for _, path in sorted(rows, key=lambda r: int(r[0])):
    print(path)
PY
)"
[ -n "$PACK_LIST" ] || fail "could not extract a2ac:CourtFile inventory from $ONTOLOGY"

# Leg 3: same set, same order.
if [ "$RUNNER_LIST" != "$PACK_LIST" ]; then
  echo "RUNNER-COMPLETENESS FAIL: runner list and pack inventory diverge:" >&2
  diff <(echo "$RUNNER_LIST") <(echo "$PACK_LIST") >&2 || true
  exit 1
fi

echo "RUNNER-COMPLETENESS PASS: runner exists; $(echo "$RUNNER_LIST" | wc -l | tr -d ' ') courts; list == pack inventory (order included)"
