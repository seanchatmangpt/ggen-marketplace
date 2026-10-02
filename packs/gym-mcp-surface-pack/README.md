# gym-mcp-surface-pack

The single MCP tool-surface kernel pack. One copy of every shared asset —
`shapes/mcp_surface.shacl.ttl`, `gates/010_mcp_authority_boundary.rq`,
`templates/mcp_tool_surface.rs.tmpl` (owns `src/mcp_tool_surface.rs`),
`templates/mcp_tools_list.json.tmpl` (owns `mcp/tools_list.json`), and the
`verification/` pair — consolidated (2026-10-01, v26.9.30 wave) from the
three-way duplication in `gym-mcp-surface-pack` + `ggen-ecosystem-mcp-surface-pack`
+ `autofde-lab-mcp-surface-pack`, where those four/five files were byte-identical
(md5-verified pre-absorption) and the output targets collided three ways.

## Layout

| path | content |
|---|---|
| `ontology.ttl` | kernel self-description (one `urn:gymmcp:McpServer`, 2 read operations) — the pack's own runnable projection surface |
| `ontology/ggen-ecosystem.ttl` | family module: the ggen CLI's 82-operation surface, DERIVED from `ggen graph --introspect` (verbatim from the absorbed pack) |
| `ontology/autofde-lab.ttl` | family module: AutoFDE Lab's 4-operation OpenClaw bridge surface, DERIVED from the real `_TOOL_SPECS` (verbatim from the absorbed pack) |
| `shapes/`, `gates/`, `templates/`, `verification/` | the single kernel copies (byte-identical ×3 before absorption) |
| `families/ggen-ecosystem.md` | family note: provenance + regeneration cadence |
| `families/autofde-lab.md` | family note: provenance + regeneration cadence |
| `families/ggen-ecosystem/derive_ggen.py` | derivation script; writes the module ontology to `argv[1]` |
| `families/autofde-lab/derive_autofde.py` | derivation script; writes the module ontology to `argv[1]` |
| `witnesses/fail/*.ttl` | anti-vacuity witnesses: each must make `gates/010_mcp_authority_boundary.rq` fire |
| `qualification/verify.py` | the one court (kernel + each module + fail witnesses + union guard) |

## One server per graph (rendering contract)

`gates/010_mcp_authority_boundary.rq` refuses any graph holding two
`urn:gymmcp:McpServer` nodes (`multiple-mcp-server-nodes-refused`): two server
nodes in one graph would silently emit two conflicting `MCP_TOOLS` tables.
Consequence, and this is deliberate: the kernel graph and each family module
render **standalone**, never merged. One rendering graph = one server = one
namespace. The court proves both directions (each graph alone is silent;
kernel+module union fires).

## Output targets

`src/mcp_tool_surface.rs` and `mcp/tools_list.json` are owned by the kernel
templates. A family consumer points ggen at its module ontology
(`ontology/<family>.ttl`) and these templates; the module's server node
(`dct:identifier` `ggen` / `autofde_lab`) parametrizes the same projection
the kernel's self-description gets. No per-family template copies exist.

## Family modules and cadence

- **ggen-ecosystem** — live-introspect cadence. Regenerate after any ggen CLI
  verb-surface change: `python3 families/ggen-ecosystem/derive_ggen.py ontology/ggen-ecosystem.ttl`
  (shells out to the installed `ggen graph --introspect`; see the family note
  for the auditable READ/DO classification rule).
- **autofde-lab** — curated cadence. Regenerate when AutoFDE Lab's
  `openclaw_bridge.py::_TOOL_SPECS` or `openclaw.plugin.json` changes:
  `python3 families/autofde-lab/derive_autofde.py ontology/autofde-lab.ttl`
  (parses the real vendor tree via `ast`; no scikit-decide import).

The cadence difference is load-bearing: ggen's surface is re-readable on demand
from the tool itself; autofde-lab's is read from a vendor tree snapshot, so its
module carries `prov:wasDerivedFrom` plus the exact source version facts
(`dct:hasVersion`) and is re-derived only on a recorded upstream change.

## Consumer join

Instance ontologies reference the kernel vocabulary (`urn:gymmcp:*`,
`urn:gymact:consequence:read|do`) by IRI literal — the capability-ecology
dotted-ID pattern. There is no `owl:imports` and no cross-pack import; the join
is the shared IRI space itself, checked by the court's per-module gate runs.

## Authority boundary

Unchanged from the pre-absorption packs: these templates manufacture MCP tool
*intents* only. Every DO operation carries `urn:gymmcp:requiresAdmission true`
and the gate refuses any DO operation without it. Consequential execution stays
behind GymAct/BRCE admission.

## Supersession

Absorbs `ggen-ecosystem-mcp-surface-pack` and `autofde-lab-mcp-surface-pack`
(both 26.9.1). Their unique assets moved verbatim (module ontologies via
`git mv`, derivation scripts via `git mv`); their byte-identical kernel copies
were deleted with the packs. Per-family `ggen.toml` project manifests
(`ggen-ecosystem-mcp-surface`, `autofde-lab-mcp-surface` project names) are gone:
a module renders through the kernel's `ggen.toml` + module ontology, not through
a second manifest. `packs/elixir-mcp-a2a-pack/pack.toml` mentions
`gym-mcp-surface-pack` by name only (no path pin) and needs no edit; both
absorbed pack names were not referenced by any other pack's pack.toml.
