#!/usr/bin/env bash
# T03 invalid corpus — symlink fixture attack injector
# RFC-GPACK-001 v26.9.17 §72: symlinks inside pack source are refused
# (REFUSED:PACK_SYMLINK). This script MATERIALIZES that attack by creating
# templates/linked-source.tera as a symlink to ../pack.toml inside the pack
# copy given as $1 (default: this fixture directory).
#
# LAW (ticket acceptance #3): no real symlink is ever committed to git.
# Prefer running this against a scratch copy — assert/run.sh always does.
# Running it in-tree creates a symlink under packs/, which the
# marketplace's own PACK_SYMLINK gate (scripts/marketplace.py) will
# (correctly) refuse until you delete it.
#
# Usage: setup.sh [pack-copy-dir]
set -eu
TARGET_DIR="${1:-}"
if [ -z "$TARGET_DIR" ]; then
  TARGET_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  echo "WARNING: attacking the in-tree pack at $TARGET_DIR — prefer a scratch copy (see README)." >&2
fi
mkdir -p "$TARGET_DIR/templates"
ln -sfn ../pack.toml "$TARGET_DIR/templates/linked-source.tera"
echo "materialized §72 attack: $TARGET_DIR/templates/linked-source.tera -> ../pack.toml"
