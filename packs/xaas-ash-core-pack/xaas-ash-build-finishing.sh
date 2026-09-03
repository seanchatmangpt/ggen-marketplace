#!/usr/bin/env bash
# xaas-ash-build-finishing.sh -- Part 5: real, project-wide finishing commands.
# Run from the target Ash project. The master runner preserves that working
# directory and invokes this script by absolute path.
set -euo pipefail

echo "=== XaaS project-wide finishing pass: $(date) ==="

# NOTE (v0.3.0 rewrite): the CapabilityClass enum and the Xaas.Resource base
# resource are now ggen-rendered from real ontology facts, in
# xaas-ash-build-enum-GENERATED.sh and xaas-ash-build-base-resource-GENERATED.sh
# respectively -- run those (Part 0, before Part 1's resources) instead of
# duplicating them here. The Interface enum (cli/api/mcp/a2a) is kept
# hand-assembled below since ce:interface's real value set isn't yet pulled
# through the xar: bridge ontology.
mix ash.gen.enum Xaas.Governance.Types.Interface cli,api,mcp,a2a --short-name interface --yes

# Real, confirmed task: dynamically discovers and updates Ash domains in
# config.exs (idempotent to re-run after adding/removing domains across
# Parts 1-4).
mix ash.set.domains --yes

# Real diagram generation per domain (requires local Mermaid CLI).
#
# BUG FIX (speedrun-confirmed, real failure, independently re-confirmed by a
# parallel session): `--yes` is not a supported flag for this task -- it does
# not accept Igniter's global --yes flag. Confirmed by the speedrun's own
# captured error output ("--yes : Unknown option"; real schema only accepts
# --format/-f, --only/-o, --type/-t).
mix ash.generate_resource_diagrams

mix compile

echo "=== Finishing pass complete: $(date) ==="
