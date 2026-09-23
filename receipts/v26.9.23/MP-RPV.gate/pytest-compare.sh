#!/usr/bin/env bash
# No new test failures: run the repo suite at the worktree head, run the tests that failed there on a
# git archive of the base, and exit 0 iff every head failure also fails at the base.
# Usage: bash pytest-compare.sh <worktree> <base sha> <scratch dir>
WT=$1; BASE=$2; SC=$3
mkdir -p "$SC/base-tree"
(cd "$WT" && python3 -m pytest tests/ scripts/ -q -p no:cacheprovider > "$SC/pytest-head.log" 2>&1); echo "head pytest exit=$?"
grep '^FAILED ' "$SC/pytest-head.log" | sed 's/ - .*//' | sort > "$SC/failed-head.txt"
tests=$(sed 's/^FAILED //' "$SC/failed-head.txt" | tr '\n' ' ')
git -C "$WT" archive "$BASE" | tar -x -C "$SC/base-tree"
(cd "$SC/base-tree" && python3 -m pytest -q -p no:cacheprovider $tests > "$SC/pytest-base.log" 2>&1); echo "base pytest exit=$?"
grep '^FAILED ' "$SC/pytest-base.log" | sed 's/ - .*//' | sort > "$SC/failed-base.txt"
rm -rf "$SC/base-tree"
tail -1 "$SC/pytest-head.log"; tail -1 "$SC/pytest-base.log"
new=$(comm -23 "$SC/failed-head.txt" "$SC/failed-base.txt")
echo "head failures: $(wc -l < "$SC/failed-head.txt")  also failing at base: $(comm -12 "$SC/failed-head.txt" "$SC/failed-base.txt" | wc -l)"
if [ -n "$new" ]; then echo "NEW FAILURES:"; echo "$new"; exit 1; fi
echo "NO_NEW_FAILURES"
