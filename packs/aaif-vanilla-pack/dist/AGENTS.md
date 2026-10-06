# AGENTS.md

> Standard Repository Guidance for ggen-marketplace Agent (Conforming to AAIF AGENTS.md Specification)

## Purpose
Autonomous semantic manufacturing pack registry, discovery, qualification, and catalog indexing agent.

## Dev Environment
Python 3.11+, Rust 1.80+, Homebrew pytest, ggen v26.9.28.

## Testing Instructions
Run Chicago-style test suite with real collaborators via pytest tests/.

## Coding Conventions
Strict adherence to typed SPARQL gates, RDF ontologies, and deterministic projections.

## Useful Commands
python3.11 scripts/marketplace.py validate, pytest tests/, ggen sync run --dry-run

## Operating Boundaries
No symlinks under packs/, fail-closed admission, zero ambient execution authority.

## Open Protocol Conformances (AAIF 6-Project Suite)
- **Agent2Agent (A2A)**: Discovery at `.well-known/agent.json`.
- **Model Context Protocol (MCP)**: Server configurations in `mcp/mcp_servers.json`.
- **Agentgateway**: L7 reverse proxy configuration in `agentgateway/config.json`.
- **Agent Router**: Envoy AI Gateway CRD manifests in `k8s/agent-router.yaml`.
- **Goose**: Local autonomous agent runtime configured in `.config/goose/config.yaml`.
- **AGENTS.md**: Standardized repository instruction format.
