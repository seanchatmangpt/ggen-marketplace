#!/usr/bin/env bash
# run_fleet_courts.sh -- thin wrapper for run_fleet_courts.py.
# Resolves to the repo root so the command works from any working directory;
# passes through all arguments and the python exit code.
#
# Machine-wide CPU-fairness limiter: the fleet courts (and witness/audit runs
# that share this entry point) spawn many doc-hdit processes; unbounded, they
# saturate the machine (measured 2026-10-09: ~4.5h wall at 24-37 concurrent
# processes at 100% CPU). The mkdir-based semaphore below caps concurrent
# holders machine-wide at DOC_HDIT_MAX_CONC (default 4) slots under
# DOC_HDIT_SEM_DIR (default /tmp/doc-hdit-semaphore), polling every 5s with a
# 30-minute acquisition timeout (exit 99 on timeout).
#
# POSIX sh. Court semantics unchanged: the script still exits 0 iff all
# courts pass (the limiter only gates entry, never the verdict).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

DOC_HDIT_SEM_DIR="${DOC_HDIT_SEM_DIR:-/tmp/doc-hdit-semaphore}"
DOC_HDIT_MAX_CONC="${DOC_HDIT_MAX_CONC:-4}"
DOC_HDIT_SEM_TIMEOUT="${DOC_HDIT_SEM_TIMEOUT:-1800}"  # seconds

# acquire_sem -- take one slot in the machine-wide semaphore or time out.
acquire_sem() {
  mkdir -p "$DOC_HDIT_SEM_DIR"
  local waited=0
  while :; do
    local slot=0
    while [ "$slot" -lt "$DOC_HDIT_MAX_CONC" ]; do
      if mkdir "$DOC_HDIT_SEM_DIR/slot.$slot" 2>/dev/null; then
        SLOT_FILE="$DOC_HDIT_SEM_DIR/slot.$slot"
        return 0
      fi
      slot=$((slot + 1))
    done
    if [ "$waited" -ge "$DOC_HDIT_SEM_TIMEOUT" ]; then
      echo "run_fleet_courts: semaphore timeout after ${waited}s" >&2
      return 99
    fi
    sleep 5
    waited=$((waited + 5))
  done
}

release_sem() {
  [ -n "${SLOT_FILE:-}" ] && rmdir "$SLOT_FILE" 2>/dev/null || true
}

# with_sem CMD... -- run CMD holding one semaphore slot.
with_sem() {
  acquire_sem || return $?
  trap release_sem EXIT
  "$@"
}

if [ "${1:-}" = "--probe-limiter" ]; then
  # Synthetic probe: 6 background stub jobs through the limiter; prints
  # start/end timestamps per job. Witness gate: at most
  # $DOC_HDIT_MAX_CONC overlap at any instant.
  echo "probe begin $(date +%s) max=$DOC_HDIT_MAX_CONC dir=$DOC_HDIT_SEM_DIR"
  probe_job() {
    with_sem sh -c '
      echo "job $$ start $(date +%s.%N)"
      sleep 3
      echo "job $$ end   $(date +%s.%N)"
    '
  }
  pids=""
  i=0
  while [ "$i" -lt 6 ]; do
    probe_job &
    pids="$pids $!"
    i=$((i + 1))
  done
  rc=0
  for p in $pids; do wait "$p" || rc=1; done
  echo "probe end rc=$rc"
  exit "$rc"
fi

# Heavy invocation gated by the machine-wide limiter. exec would replace the
# shell and skip the slot release, so run in the foreground and propagate rc.
with_sem python3 "$REPO_ROOT/scripts/run_fleet_courts.py" "$@"
exit $?
