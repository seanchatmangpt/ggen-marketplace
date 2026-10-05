# AGENTS.md

> Standard Repository Guidance for Marketplace Coordinator (Conforming to AAIF AGENTS.md Specification)

## Purpose
Swarm intake, task delegation, and work order orchestration agent.

## Dev Environment
Python 3.11+, Rust 1.80+, Homebrew pytest, ggen v26.9.28.

## Testing Instructions
Run Chicago-style multi-agent test courts with pytest tests/.

## Coding Conventions
Strict compliance with AAIF open standards (A2A, MCP, Agentgateway, Router, Goose, AGENTS.md).

## Useful Commands
pytest tests/test_aaif_vanilla_pack_court.py, python3.11 scripts/marketplace.py validate aaif-vanilla-pack

## Operating Boundaries
Fail-closed admission, no ambient execution authority, immutable receipt logs.

## Open Protocol Conformances (AAIF 6-Project Suite)
- **Agent2Agent (A2A)**: Discovery at `.well-known/agent.json`.
- **Model Context Protocol (MCP)**: Server configurations in `mcp/mcp_servers.json`.
- **Agentgateway**: L7 reverse proxy configuration in `agentgateway/config.json`.
- **Agent Router**: Envoy AI Gateway CRD manifests in `k8s/agent-router.yaml`.
- **Goose**: Local autonomous agent runtime configured in `.config/goose/config.yaml`.
- **AGENTS.md**: Standardized repository instruction format.