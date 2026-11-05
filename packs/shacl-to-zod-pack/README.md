# shacl-to-zod-pack

Projects admitted SHACL NodeShapes into JavaScript Zod schemas. Target pack for
`shacl-projection-pack` law: composes it (pack-to-pack dependencies are not declarable in
pack.toml — the consumer composes both), renders `src/shacl_zod_schemas.js`, ships zero
domain individuals.

## What It Projects

- `src/shacl_zod_schemas.js` — one `export const <sp:schemaName> = z.object({...})` per
  `sp:ZodSchema` individual in the merged graph (imports `zod`)

Field mapping (reuses shacl-projection-pack vocabulary, namespace
`http://seanchatmangpt.github.io/packs/shacl-projection#`):

| consumer fact | projection |
|---|---|
| `sh:datatype xsd:string` | `z.string()` |
| `sh:datatype xsd:boolean` | `z.boolean()` |
| `sh:datatype xsd:integer` / `xsd:long` | `z.number().int()` |
| any other `sh:datatype` | `z.number()` |
| `sh:in` list | `z.enum(["...", ...])` |
| `sp:nullable true` | `.nullable()` |
| `sp:collection true` | `z.array(...)` |
| `sh:node` nested shape | `z.lazy(() => <sp:projectionName>)` |

## Consumer Contract

npm deps: `zod` — `src/shacl_zod_schemas.js` imports `zod`; there is no other third-party
import in any template (verified by grep over `templates/`). Deleting `zod` is load-bearing:
strict `tsc` fails with `TS2307 Cannot find module 'zod'` (witnessed this session, see
receipt F2.md step 9).

Beyond npm deps, the consumer must:

- mint its own `sp:ZodSchema` individuals in its ontology (`sp:schemaName` legal JS
  identifier, `sp:derivedFromShape` → a real `sh:NodeShape`). The pack ships zero
  individuals; **zero individuals is a silent stub** — the template still renders a file
  containing only the `zod` import (witnessed in cmms: `src/shacl_zod_schemas.js` is a
  2-line stub);
- compose `shacl-projection-pack` for shape-validity law (missing/ambiguous value kinds,
  invalid datatypes, unresolved nested shapes);
- supply `sp:projectionName` on any nested shape referenced via `sh:node`;
- supply `sp:nullable` / `sp:collection` as boolean literals (`"false"` string forms are
  the COALESCE default, so absent = false).

Vocabulary note: this pack's SPARQL selects `sp:ZodSchema` / `sp:schemaName`, while
shacl-projection-pack's own qualification individuals use `shp:SchemaModel` /
`shp:className`. Same namespace, different properties — a consumer supplying only
`shp:SchemaModel` individuals gets the stub. This is registered as a known interop gap
(receipt F2.md), not silently papered over.

## Output Paths Are Template-Authored (truth-telling)

The render target is the `to:` line in `templates/shacl_to_zod.js.tmpl` — currently
`src/shacl_zod_schemas.js`. **A consumer cannot retarget it from `ggen.toml`**: there is no
output-path override in the manifest schema; witnessed this session, a consumer manifest
desiring `src/shacl_zod_schemas.ts` still received `src/shacl_zod_schemas.js` (both files
exist in that consumer; the `.ts` copy was hand-authored, not projected).

To retarget, vendor the template into the consumer's own `[templates].dir` and edit its
`to:` line — the pack binds templates by path, so the consumer's copy wins for that
consumer. Do not hand-edit the projected output.

## Gates

- `gates/010_template_literal_scan.py` — fail-closed literal scan: no banned domain
  literals in `templates/`, and no hardcoded `export const X =` (projected exports must
  come from the graph via `{{ ... }}`). Any hit exits 1; a missing or unreadable templates
  dir also exits 1. Anti-vacuity flip witnessed in receipt F2.md.

## See Also

- `packs/shacl-projection-pack/README.md` — the shared law and its gates
