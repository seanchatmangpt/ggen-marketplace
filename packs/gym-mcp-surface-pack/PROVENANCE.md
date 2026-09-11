# Source provenance

Derived from `chatgptgym-gymact-bridge-pack` (this marketplace), specifically
`templates/mcp_tool_schema.rs.tmpl` and `gates/010_execution_boundary.rq`. That pack
is not modified by this one; this pack is additive.

## What was generalized, and why it had to be

Run for real with `ggen 26.8.28`: the reference `mcp_tool_schema.rs.tmpl`, given
AutoFDE Lab's real operation graph unchanged, emits

```
McpToolSchema { name: "chatgptgym.catalog", consequence_class: "Read" },
McpToolSchema { name: "chatgptgym.describe", consequence_class: "Read" },
McpToolSchema { name: "chatgptgym.match",   consequence_class: "Do" },
McpToolSchema { name: "chatgptgym.run",     consequence_class: "Do" },
```

into `src/chatgptgym_mcp_tools.rs`. Three defects, all of them template-local rather
than graph-local:

1. **Namespace is a template literal.** Every gym's tools are stamped `chatgptgym.`.
2. **Output path is a template literal.** Every gym writes `chatgptgym_*.rs`.
3. **Descriptions and parameters are dropped.** AutoFDE Lab's real bridge carries 4
   descriptions and 9 typed parameters; the reference projection emits name plus
   consequence class only, which is not enough for an MCP host to advertise a
   callable tool.

And the boundary gate does not travel either. `010_execution_boundary.rq` run against
AutoFDE Lab's real graph refuses **all four** of its real operations — `catalog` and
`describe` as `non-observational-read-refused` (they do not start with `inspect-`),
`match` and `run` as `ambient-do-authority-refused` (they are not in the literal
`simulate-capability|reset-simulation` whitelist).

This pack moves all four things into the graph: namespace, description, parameters,
and the admission obligation. `gates/010_mcp_authority_boundary.rq` enforces the same
authority boundary as a *graph obligation* — a DO operation may be projected only if
the graph states `urn:gymmcp:requiresAdmission true` — with no pack-local name list,
plus three checks the reference gate has no analogue for (a DO operation claiming
replay safety, a READ operation demanding admission, two server nodes in one graph).

## Vocabulary reuse

Reused: `dct:` (title/description/type/identifier/hasVersion), `sosa:Procedure` for
an operation exactly as the reference pack models it, `prov:wasDerivedFrom`, `skos:`
for concept labels, `sh:` for the profile. The GymAct consequence concepts
`<urn:gymact:consequence:read|do>` are reused verbatim so a gym already classified
for GymAct needs no reclassification to gain an MCP projection.

Minted only where no public vocabulary covers the concept: `urn:gymmcp:McpServer`,
`urn:gymmcp:Parameter`, `urn:gymmcp:hasParameter`, `urn:gymmcp:required`,
`urn:gymmcp:replaySafe` (grounded in AutoFDE Lab's real `openclaw.plugin.json`
`toolMetadata` flags), `urn:gymmcp:requiresAdmission`.

## Authority boundary

Unchanged from the reference pack: these templates manufacture MCP tool *intents*.
They carry no runtime actuation authority and invoke nothing. Consequential DO
remains external, behind GymAct/BRCE admission.

## Verification

- `verification/run_gate.py <graph.ttl> gates/010_mcp_authority_boundary.rq` — exits
  non-zero on any refusal row.
- `verification/verify_surface.rs` — Chicago-style checks against the real generated
  module (no test doubles; the module under test is the real generated file).
  Replace `GENERATED_PATH` with the absolute path to a generated
  `src/mcp_tool_surface.rs`, then `rustc --edition 2021`.
