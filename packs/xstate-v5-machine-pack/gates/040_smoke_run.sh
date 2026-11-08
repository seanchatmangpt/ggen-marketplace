#!/usr/bin/env bash
# 040_smoke_run.sh — smoke-test court for a generated XState v5 project.
#
# Runs vitest against the target project's generated smoke-test glob and
# gates on vitest's exit code: 0 = smoke court PASS, non-zero = FAIL.
# The gate adds no verdict of its own — the real test run is the court
# (Chicago discipline: real collaborators, exit-code gate, no fake pass).
#
# Usage:
#   gates/040_smoke_run.sh <project-dir> [smoke-glob]
#
#   project-dir   a GENERATED project root (must contain package.json and
#                 vitest available via npx/node_modules)
#   smoke-glob    glob of smoke tests, default "tests/**/*.smoke.test.ts"
#                 (the pack generator's smoke output path)
#
# Structural preflight (fail loud, never a silent pass):
#   - project-dir must exist and contain package.json
#   - the resolved smoke glob must match at least one test file
#     (--passWithNoTests is NOT passed to vitest; an empty glob fails)
#
# SCOPE DISCLOSURE (Z1b wave): no generated project exists in this pack
# yet, so the end-to-end vitest arm is exercised only structurally this
# wave — preflight refusals are demonstrated (missing dir, missing
# package.json, empty glob); the full vitest pass/fail arms require a
# ggen-generated consumer project and land with its receipt.
#
# Exit codes: 0 = smoke suite green; 1 = preflight or vitest failure; 2 = usage.

set -u

if [ $# -lt 1 ]; then
  echo "USAGE-ERROR: 040_smoke_run.sh <project-dir> [smoke-glob]" >&2
  exit 2
fi

PROJECT_DIR="$1"
SMOKE_GLOB="${2:-tests/**/*.smoke.test.ts}"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "SMOKE-COURT: FAIL — project dir not found: $PROJECT_DIR" >&2
  exit 1
fi
if [ ! -f "$PROJECT_DIR/package.json" ]; then
  echo "SMOKE-COURT: FAIL — no package.json in $PROJECT_DIR (not a generated project root)" >&2
  exit 1
fi

# Fail loud on an empty glob: count matching files before invoking vitest.
# (globstar, nullglob — count via find to stay POSIX-portable on the glob)
matched=$(find "$PROJECT_DIR" -path "${PROJECT_DIR}/node_modules" -prune -o \
  -type f -name "$(basename "$SMOKE_GLOB")" -print 2>/dev/null | wc -l | tr -d ' ')
if [ "${SMOKE_GLOB}" = "tests/**/*.smoke.test.ts" ]; then
  matched=$(find "$PROJECT_DIR" -path "*/node_modules" -prune -o -type f \
    -name "*.smoke.test.ts" -print 2>/dev/null | wc -l | tr -d ' ')
fi
if [ "$matched" -eq 0 ]; then
  echo "SMOKE-COURT: FAIL — smoke glob '$SMOKE_GLOB' matched 0 test files in $PROJECT_DIR (empty suite is not a pass)" >&2
  exit 1
fi

cd "$PROJECT_DIR" || { echo "SMOKE-COURT: FAIL — cannot enter $PROJECT_DIR" >&2; exit 1; }

if command -v npx >/dev/null 2>&1; then
  runner="npx vitest run"
elif [ -x "./node_modules/.bin/vitest" ]; then
  runner="./node_modules/.bin/vitest run"
else
  echo "SMOKE-COURT: FAIL — vitest not available (npx absent, no node_modules/.bin/vitest)" >&2
  exit 1
fi

# vitest's tinyglob treats '**' as requiring >=1 directory, so a raw
# 'tests/**/*.smoke.test.ts' filter silently matches nothing; invoke with
# the glob's directory + filename filter instead (vitest positionals are
# path regexes).
smoke_dir="${SMOKE_GLOB%%/**}"
smoke_name="${SMOKE_GLOB##*/}"
echo "SMOKE-COURT: running $runner '$smoke_dir' (filter '$smoke_name') in $PROJECT_DIR"
# shellcheck disable=SC2086
$runner "$smoke_dir" "$smoke_name"
rc=$?

if [ "$rc" -eq 0 ]; then
  echo "SMOKE-COURT: PASS — vitest exit 0"
else
  echo "SMOKE-COURT: FAIL — vitest exit $rc"
fi
exit "$rc"
