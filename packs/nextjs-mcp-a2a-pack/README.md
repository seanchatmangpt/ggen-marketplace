# nextjs-mcp-a2a-pack

Standard ggen-marketplace pack for projecting typed MCP (Model Context Protocol)
tool registries and A2A (Agent-to-Agent) agent fleet declarations as
TypeScript data modules, from an RDF ontology. Ships law + templates only:
the consumer supplies all individuals.

## Capabilities

- **Zero-Unreceipted Actuation Law**: Tool authority is bounded to
  `READ_ONLY` or `PROPOSAL` by gate `020_tool_authority.rq`; the projected
  registry carries the authority bound as a typed field.
- **Air-Gap Invariant**: Loopback-only endpoint law is declared in the
  ontology (`nma:McpServer` / `nma:endpoint`); consumers project endpoints
  from their own graph.
- **Agent Completeness Gate**: `010_agent_completeness.rq` refuses an
  `nma:A2AAgent` missing `agentId`, `agentName`, `personaPrompt`, or
  `defaultModel`.
- **Strict Separation**: Carries no downstream application-specific
  assumptions; admits consumers by projection.

## Generated Artifacts (exactly two)

- `generated/mcp-registry.ts`: `GENERATED_MCP_TOOLS` — typed tool
  definitions (`name`, `description`, `authority`, `inputSchema`) projected
  from `nma:McpTool` individuals.
- `generated/a2a-fleet.ts`: `GENERATED_A2A_FLEET` — typed agent personas
  (`id`, `name`, `role`, `defaultModel`, `personaPrompt`) projected from
  `nma:A2AAgent` individuals.

Both are self-contained typed-data modules: zero imports of any kind, zero
side effects.

## Consumer Contract

- `runtime = []` — no npm dependencies. The projected artifacts import
  nothing; they are valid TypeScript in any strict-mode project as-is.
- The consumer declares `nma:McpTool` / `nma:A2AAgent` individuals (with the
  properties required by gates 010/020) in its own ontology graph and
  composes this pack in its `ggen.toml` `[packs]` section; gates run over
  the merged graph at sync time.
- Route handlers, execution harnesses, and self-play engines are
  consumer-side; this pack projects data only.

## Gates

- `gates/010_agent_completeness.rq` — every `nma:A2AAgent` must have
  `agentId`, `agentName`, `personaPrompt`, `defaultModel`.
- `gates/020_tool_authority.rq` — every `nma:McpTool` must have
  `toolName`, `toolDescription`, `inputSchemaJson`, and `authority` in
  `READ_ONLY | PROPOSAL`.

Gates are SPARQL SELECT gates executed by ggen during sync; sync exit 0
means gates passed.

## Court

`ggen sync run` must exit 0 and reproduce both artifacts byte-stably; each
projected artifact is then imported and executed (Node type-stripping) and
its exports asserted. Passes with zero unresolved imports because the
artifacts ship zero imports — no `tsc` pass is required. The anti-vacuity
flip is structural: there is no dependency whose removal would flip the
result, so the court asserts the zero-import property directly (grep)
rather than by mutation.
