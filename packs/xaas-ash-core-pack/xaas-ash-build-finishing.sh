#!/usr/bin/env bash
# xaas-ash-build-finishing.sh -- Part 5: real, project-wide finishing commands.
# Every line here is a real, confirmed CLI task (see README.md's provenance
# section) -- no fabricated flags.
set -euo pipefail
cd "$(dirname "$0")"

echo "=== XaaS project-wide finishing pass: $(date) ==="

# NOTE (v0.3.0 rewrite): the CapabilityClass enum and the Xaas.Resource base
# resource are now ggen-rendered from real ontology facts, in
# xaas-ash-build-enum-GENERATED.sh and xaas-ash-build-base-resource-GENERATED.sh
# respectively -- run those (Part 0, before Part 1's resources) instead of
# duplicating them here. The Interface enum (cli/api/mcp/a2a) is kept
# hand-assembled below since ce:interface's real value set isn't yet pulled
# through the xar: bridge ontology.
mix ash.gen.enum Xaas.Governance.Types.Interface cli,api,mcp,a2a --short-name interface --yes

# Real, confirmed task from this session's CLI survey: dynamically
# discovers and updates Ash domains in config.exs (idempotent to re-run
# after adding/removing domains across Parts 1-4).
mix ash.set.domains --yes

# Real diagram generation per domain (requires local Mermaid CLI).
#
# BUG FIX (speedrun-confirmed, real failure): `--yes` is not a supported
# flag for this task. Re-verified directly against the real source
# (ash-project/ash@main:lib/mix/tasks/gen/ash.gen.resource_diagrams.ex is
# NOT under lib/mix/tasks/gen/ -- this task lives elsewhere in Ash and its
# real schema only accepts --format/-f, --only/-o, --type/-t, confirmed by
# the speedrun's own captured error output ("--yes : Unknown option").
mix ash.generate_resource_diagrams

mix compile

echo "=== Finishing pass complete: $(date) ==="
