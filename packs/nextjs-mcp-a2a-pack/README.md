# nextjs-mcp-a2a-pack

Standard ggen-marketplace pack for manufacturing Model Context Protocol (MCP) tool endpoints,
Agent-to-Agent (A2A) protocol routers, and autonomous multi-agent self-play testing surfaces
in Next.js 16+ App Router applications.

## Capabilities

- **Zero-Unreceipted Actuation**: Enforces cryptographic receipt minting (SHA-256) for all A2A and MCP interactions.
- **Air-Gap Invariant**: Restricts MCP tool invocations to local loopback endpoints (`127.0.0.1`, `localhost`).
- **Autonomous Self-Play Testing**: Runs multi-turn adversarial or collaborative agent debates with `z.ai` (Zhipu AI GLM-4.6) or hermetic offline simulators.
- **Strict Separation**: Carries no downstream application-specific assumptions; admits consumers by projection.

## Generated Artifacts

- `src/lib/mcp/generated-tools.ts`: Type-safe tool definitions and loopback execution harness.
- `src/lib/a2a/generated-fleet.ts`: Declared agent personas with bounded CONSTRUCT prompts.
- `src/lib/a2a/self-play-engine.ts`: Multi-agent self-play orchestrator.
- `src/app/api/mcp/route.ts`: App router endpoint for MCP tool execution.
- `src/app/api/a2a/self-play/route.ts`: App router endpoint for autonomous multi-turn simulations.
