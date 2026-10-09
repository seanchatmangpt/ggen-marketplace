#!/usr/bin/env bash
# run_fleet_courts.sh -- thin wrapper for run_fleet_courts.py.
# Resolves to the repo root so the command works from any working directory;
# passes through all arguments and the python exit code.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$REPO_ROOT/scripts/run_fleet_courts.py" "$@"
