#!/usr/bin/env bash
# xaas-ash-build-finishing.sh -- Part 5: real, project-wide finishing commands.
# Every line here is a real, confirmed CLI task (see README.md's provenance
# section) -- no fabricated flags.
set -euo pipefail
cd "$(dirname "$0")"

echo "=== XaaS project-wide finishing pass: $(date) ==="

# Real ce:CapabilityClass enum (OBSERVE/SELECT/CONSTRUCT/DO) from
# chatman-ecosystem/ontology/capabilities.ttl's real ce:CapabilityClass
# individuals -- confirmed via that file's own TBox, not invented.
mix ash.gen.enum Xaas.Governance.Types.CapabilityClass observe,select,construct,do --short-name capability_class --yes

# Real ce:Interface enum (CLI/API/MCP/A2A), same source file.
mix ash.gen.enum Xaas.Governance.Types.Interface cli,api,mcp,a2a --short-name interface --yes

# Shared base resource -- real generator, confirmed useful given all 44
# resources share the same requested_by/approved_by/status shape.
mix ash.gen.base_resource Xaas.Resource --yes

# Real, confirmed task from this session's CLI survey: dynamically
# discovers and updates Ash domains in config.exs (idempotent to re-run
# after adding/removing domains across Parts 1-4).
mix ash.set.domains --yes

# Real diagram generation per domain (requires local Mermaid CLI).
mix ash.generate_resource_diagrams --yes

mix compile

echo "=== Finishing pass complete: $(date) ==="
