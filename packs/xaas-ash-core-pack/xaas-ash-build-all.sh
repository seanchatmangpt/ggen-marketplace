#!/usr/bin/env bash
# xaas-ash-build-all.sh -- canonical master runner.
#
# Usage:
#   bash xaas-ash-build-all.sh /path/to/ash-project
#
# The ggen-rendered scripts are the executable source for row-driven Ash
# construction. Ecosystem installation and the finishing pass remain fixed,
# cross-cutting command programs because they are not per-capability rows.
set -euo pipefail

PACK_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="${1:-$PWD}"

if [[ ! -f "$TARGET_DIR/mix.exs" ]]; then
  echo "REFUSED:XAAS_TARGET_NOT_MIX_PROJECT:$TARGET_DIR" >&2
  exit 4
fi

cd "$TARGET_DIR"

echo "############################################"
echo "# XaaS Ash construction target: $TARGET_DIR"
echo "# Part 1: ggen-rendered base resources (45 mix commands)"
echo "############################################"
bash "$PACK_DIR/xaas-ash-build-base-GENERATED.sh"

echo "############################################"
echo "# Part 2: ecosystem package installation (22 mix commands)"
echo "############################################"
bash "$PACK_DIR/xaas-ash-build-ecosystem.sh"

echo "############################################"
echo "# Part 3: ggen-rendered extension projection (49 mix commands)"
echo "############################################"
bash "$PACK_DIR/xaas-ash-build-extend-GENERATED.sh"

echo "############################################"
echo "# Part 4: ggen-rendered changes/validations (89 mix commands)"
echo "############################################"
bash "$PACK_DIR/xaas-ash-build-changes-GENERATED.sh"

echo "############################################"
echo "# Part 5: project-wide finishing pass (6 mix commands)"
echo "############################################"
bash "$PACK_DIR/xaas-ash-build-finishing.sh"

echo "############################################"
echo "# ALL PARTS COMPLETE -- 211 canonical mix commands executed"
echo "############################################"
