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
echo "# Part 0: ggen-rendered base resource + enum (must precede Part 1 -- the"
echo "# base_resource rewrite mechanism only rewrites use-sites that exist"
echo "# AFTER it runs, per ash.gen.base_resource.ex's own"
echo "# Igniter.update_all_elixir_files/2 semantics, source-confirmed)"
echo "############################################"
bash "$PACK_DIR/xaas-ash-build-base-resource-GENERATED.sh"
bash "$PACK_DIR/xaas-ash-build-enum-GENERATED.sh"

echo "############################################"
echo "# Part 1: ggen-rendered base resources (44 mix commands, --extend ets)"
echo "############################################"
bash "$PACK_DIR/xaas-ash-build-base-GENERATED.sh"

echo "############################################"
echo "# Part 2: ecosystem package installation (postgres/json_api/graphql/etc)"
echo "############################################"
bash "$PACK_DIR/xaas-ash-build-ecosystem.sh"

echo "############################################"
echo "# Part 3: ggen-rendered extension projection (49 mix commands --"
echo "# real ets -> postgres,json_api,graphql extend, now that Part 2"
echo "# installed those packages)"
echo "############################################"
bash "$PACK_DIR/xaas-ash-build-extend-GENERATED.sh"

echo "############################################"
echo "# Part 3.5: ggen-rendered codegen + migrate (real AshPostgres migration"
echo "# generation + execution -- must run after Part 3's postgres extend;"
echo "# requires a real reachable Postgres via config/dev.exs DATABASE_URL)"
echo "############################################"
bash "$PACK_DIR/xaas-ash-build-codegen-migrate-GENERATED.sh"

echo "############################################"
echo "# Part 4: ggen-rendered changes/validations (89 mix commands -- stub"
echo "# scaffolding, requires hand-authored completion, see README.md)"
echo "############################################"
bash "$PACK_DIR/xaas-ash-build-changes-GENERATED.sh"

echo "############################################"
echo "# Part 5: project-wide finishing pass"
echo "############################################"
bash "$PACK_DIR/xaas-ash-build-finishing.sh"

echo "############################################"
echo "# Part 6: MCP server scaffold (ash_ai.gen.mcp) -- REAL NO-OP UNLESS A"
echo "# PHOENIX ROUTER ALREADY EXISTS. Nothing in Parts 0-5 creates one (this"
echo "# project has no router.ex/endpoint.ex as of this pack's last audit) --"
echo "# running this now will silently do nothing, which is the correct,"
echo "# honest behavior per ash_ai.gen.mcp's own source, not a bug to route"
echo "# around here. Kept last, run-if-applicable, not treated as required."
echo "############################################"
bash "$PACK_DIR/xaas-ash-build-mcp-GENERATED.sh"

echo "############################################"
echo "# ALL PARTS COMPLETE"
echo "############################################"
