# shacl-projection-pack

Shared, target-agnostic law for SHACL-shape-driven projection. Reuses standard SHACL directly
(`sh:NodeShape`, `sh:path`, `sh:datatype`, `sh:node`) and adds a minimal projection vocabulary
(`shp:derivedFromShape`, `shp:isPrimaryOutput`, `shp:nullable`, `shp:SchemaModel`,
`shp:className`). Ships zero domain individuals: composing it cannot inject any shape,
projection, or field into a consumer's output.

## What It Projects

- `src/shacl_zod_schemas.ts` — zod schemas + inferred types from `shp:SchemaModel` facts
  (imports `zod`)
- `schemas/shacl_projection.schema.json` — JSON Schema draft 2020-12 projection of the same
  facts
- `docs/shacl-projection-vocab.md` — static reference for the `shp:` vocabulary

## Consumer Contract

npm deps: `zod` + `typescript` — `src/shacl_zod_schemas.ts` imports `zod`; there is no other
third-party import in any template (verified by grep over `templates/`). Deleting `zod` from
`node_modules` is load-bearing: strict `tsc` fails with `TS2307 Cannot find module 'zod'` on
the projected file.

Beyond npm deps, the consumer must:

- supply its own `sh:NodeShape` + `shp:SchemaModel` individuals in its ontology (the pack
  ships zero individuals — the shared gates 010/020 run over the merged graph);
- compose a target pack (e.g. `shacl-to-zod-pack`, `shacl-to-pydantic-pack`) when it wants
  that target's templates — pack-to-pack dependencies are not declarable in pack.toml.

## Gates

- `gates/010_shape_validity.rq` — every projected artifact linked via `shp:derivedFromShape`
  resolves to a real, renderable SHACL graph: exactly one value kind per field
  (`sh:datatype` XOR `sh:node`), admitted XSD types only, `sh:node` targets are real
  `sh:NodeShape`s. Any returned row is a refusal.
- `gates/020_schema_model_named.rq` — every `shp:SchemaModel` has exactly one valid
  `shp:className` identifier and an `shp:derivedFromShape` link.
- `gates/030_literal_scan.py` — fail-closed literal scan: no banned domain literals in
  `templates/` (templates must stay ontology-driven).

## Court Description

The qualification court is a real scratch consumer (this session: `/tmp/f1-consumer`):

1. Consumer `ggen.toml` binds the pack by path, `--skip-ea-admission` (no `ea.graph.json`).
2. `ggen sync run` renders `src/shacl_zod_schemas.ts` from real `shp:SchemaModel` individuals
   in the consumer's ontology.
3. Strict `tsc --noEmit` over the projection with `zod` installed — exit 0, zero unresolved
   imports.
4. Anti-vacuity flip: remove `node_modules/zod` and re-run `tsc` — exit 2, `TS2307` on the
   projection. The court flips; a court that cannot flip is FAIL.

Witnessed runs and full command/exits: `docs/jira/v26.11.5/receipts/F1.md`.
