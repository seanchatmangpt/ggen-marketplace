#!/usr/bin/env bash
# Court shim-azure-terraform -- template-mutation shim court for azure-terraform-pack.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
rc=0; bash scripts/shim_court_azure_terraform.sh || rc=$?
[ "$rc" -eq 3 ] && { echo "[SKIP] terraform binary unavailable"; exit 0; }
[ "$rc" -eq 0 ] || exit "$rc"
bash scripts/shim_court_azure_terraform.sh --self-check
