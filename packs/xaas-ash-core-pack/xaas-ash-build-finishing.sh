#!/usr/bin/env bash
# xaas-ash-build-finishing.sh -- Part 5: real, project-wide finishing commands.
# Run from the target Ash project. The master runner preserves that working
# directory and invokes this script by absolute path.
set -euo pipefail

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

# Dynamically discover and update Ash domains in config.exs after Parts 1-4.
mix ash.set.domains --yes

# Diagram generation does not accept Igniter's global --yes flag.
mix ash.generate_resource_diagrams

mix compile

echo "=== Finishing pass complete: $(date) ==="
