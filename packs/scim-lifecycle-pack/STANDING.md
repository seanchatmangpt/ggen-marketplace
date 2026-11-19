# scim-lifecycle-pack Standing

Standing: VERIFIED

## Authored (GAP4 close — 2026-11-19, ggen-author, no shell)

Real ontology / SHACL / templates landed; this is no longer an empty stub.

| Surface | Path | Notes |
|---------|------|-------|
| Ontology | `ontology.ttl` v0.2.0 | User/Group/SPC + ResourceType/Schema + lifecycle ops + HTTP cards + Ash targets + specimens |
| SHACL | `shapes/scim.shacl.ttl` | NodeShapes mirroring gates 010–080; password maxCount 0; closed httpMethod enum |
| Gates | `gates/010`…`080_*.rq` | Any row = refusal |
| Templates | `templates/*.tera` (5) | ash_semantic_map.ttl, http/schema/lifecycle catalogs, ash_resource_design.md |
| Witnesses | `witnesses/pass\|fail/*.ttl` | Anti-vacuity seeds for coordinator courts |
| Manifest | `ggen.toml` + `pack.toml` + `ea.graph.json` | Frontmatter-schema pack; empty EA admit scaffold |

## Explicit non-goals (not BLOCKED — out of pack scope)

- No Elixir `Ash.Resource` / Phoenix / ash_json_api runtime (consumer lane).
- No hex deps; no hand-rolled Rust CLI.
- No DO / provisioning authority from declaring User/Group.

## Coordinator court — 2026-11-19

CLI: `ggen` 26.11.5. Prior gate lane: [Validate SCIM pack gates](0403c9c8-2003-447d-9265-42ca0a39a0be). Follow-up: remove unknown `base_iri`; add empty `ea.graph.json` (FM-LAW-015 scaffold, same shape as `ggen init`).

| Command | EXIT | Evidence |
|---------|------|----------|
| `ggen graph validate --files ontology.ttl --shapes shapes/scim.shacl.ttl` | **0** | `files_checked:1`, `shapes_checked:1`, `shapes_conform:true`, `quads:527` (prior + re-run) |
| `ggen sync run` (after `ggen.toml` + `ea.graph.json` fix) | **0** | wrote 5 under `generated/scim/` (`ash_semantic_map.ttl`, `http_endpoint_catalog.md`, `ash_resource_design.md`, `schema_urn_registry.md`, `lifecycle_operations.md`) |
| SHACL pass `witnesses/pass/010_user_required.ttl` | **0** | prior lane: `shapes_conform:true` |
| SHACL fail `witnesses/fail/{010,040,050}_*.ttl` | **1** each | prior lane: expected refuse (MinCount / HasValue / MaxCount) |

### Config remediations landed this session

1. `ggen.toml` `[ontology]`: drop `base_iri` (FM-CONFIG-002); keep `source` / `imports` / `[ontology.prefixes]` (schema: source/imports/prefixes/aggregate).
2. `ea.graph.json`: empty `ggen.ea.graph.v1` admit so bare `ggen sync run` clears FM-LAW-015 without `--skip-ea-admission`.

### Still out of this VERIFIED scope

- SPARQL `gates/*.rq` not executed via a formal `gate-court.toml` runner.
- Consumer Ash/HTTP runtime court (pack non-goal).
