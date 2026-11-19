# ash-rls-tenant-isolation-pack Standing

Standing: VERIFIED

- Authored / gap-closed 2026-11-19 (ggen-author GAP6); coordinator verify 2026-11-19
  (ggen 26.11.5) against pack v0.1.1; GAP6 follow-up closed FM-CONFIG-003 +
  FM-TPL-017 the same day (sync EXIT=0).
- Surface closed from scaffold stub → real capital:
  - `ontology.ttl` — vocab + closed PolicyShape/TenantGuc individuals
  - `shapes/rls.shacl.ttl` — SHACL NodeShapes (path under `shapes/`; root
    `shapes.ttl` is refused by pack contract at sync)
  - `gates/010..070` — SPARQL refusal twins (any row = refuse)
  - `templates/010..040` — frontmatter migration / court / repo GUC /
    custom_statements catalog
  - `fixtures/example-consumer.ttl` + `qualification/consumer.ttl` — positive
  - `tests/mutations/*.ttl` — one falsifier per gate
- Explicit fence: closed GUC names are `app.current_tenant_id` and
  `app.rls_platform` (srve/xaas pattern). Consumers needing
  `fnox_cos.office_id` (or other product GUCs) must extend the pack vocabulary
  or author a sibling pack — `gates/030` + SHACL refuse foreign names.

## GAP6 follow-up fixes (2026-11-19)

1. `ggen.toml` → clean frontmatter schema (`[project]` + `[ontology]` +
   `[templates]` only). Dropped `[generation]` / `[validation]` /
   `base_iri` (FM-CONFIG-003 / FM-CONFIG-002). Gates remain under `gates/`
   (pack.toml prose); sync does not list `[[generation.rules]]`.
2. OPTIONAL SPARQL → Tera: templates `010` / `040` `BIND(COALESCE(...))`
   for `nullableTenant` (default false) and `platformBypass` (default true)
   plus Tera `| default(...)` guards; `030` guards `failClosedNilTenant`.
3. Preferred SHACL court is the **union** file (ontology∪qualification):
   `ggen graph validate --files` does not merge multi-file graphs, so
   per-file consumer/fixture alone fails ClassConstraintComponent on
   cross-file GUC/policy IRIs. Pack-local sync imports
   `qualification/consumer.ttl` so sync self-proof uses the same union.

## Coordinator evidence (2026-11-19, post follow-up)

cwd: `packs/ash-rls-tenant-isolation-pack`. Binary: `ggen 26.11.5`.

| Command | EXIT | Notes |
|---|---|---|
| `ggen graph validate --files ontology.ttl --shapes shapes/rls.shacl.ttl` | 0 | 192 quads, `shapes_conform: true` |
| `cat ontology.ttl qualification/consumer.ttl > /tmp/rls-union-positive.ttl` then `ggen graph validate --files /tmp/rls-union-positive.ttl --shapes shapes/rls.shacl.ttl` | 0 | Preferred consumer court: 238 quads, `shapes_conform: true` |
| `ggen sync run --skip-ea-admission` | 0 | Frontmatter OK; wrote migration / court / repo GUC / custom_statements (4 files). `clients` (no `nullableTenant` triple) renders strict policy via COALESCE default |
| rdflib gate court: ontology∪qualification → 0 rows; ontology∪each mutation → ≥1 row | 0 | 7/7 positive clean; 7/7 mutations FLIP |

VERIFIED: sync EXIT=0 and union SHACL EXIT=0.
