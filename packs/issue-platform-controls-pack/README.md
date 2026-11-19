# issue-platform-controls-pack

Standing: VERIFIED

See `STANDING.md` for exact commands and exit codes (2026-11-19, ggen
26.11.5). Authored / gap-closed 2026-11-19; GAP follow-up closed the
semantic-jira-pack dep-gate false-refuse by admitting a scoped court.

## Evidence path (coordinator court)

1. `ggen graph validate --files ontology.ttl qualification/consumer.ttl --shapes shapes/ip.shacl.ttl`
   (prefer union file: comma `--files` does not merge graphs for SHACL class
   resolution across files).
2. Per-gate rdflib (any returned row = refusal):
   - ontology ∪ `qualification/consumer.ttl` → **0** rows on `gates/010..050`
   - ontology ∪ each `tests/mutations/*.ttl` → **≥1** row on the paired gate
3. Scratch `ggen sync run --skip-ea-admission` against a pinned consumer that
   imports this pack + a **scoped** materialization of
   `~/ggen_igniter/priv/ggen/semantic-jira-pack/`:
   ```sh
   SJ_COURT=$(qualification/materialize_sj_dep_court.sh)
   # mount $SJ_COURT as [packs].semantic-jira-pack
   ```
   Real ontology (byte copy) + real `verify/*.unbound.rq` as `gates/*.rq`.
   Witness-driver `gates/` omitted (ADR-0010 witness scoring ≠ ggen
   FM-PACK-013 offender scoring). Unscoped igniter-tree mount stays red on
   `010_work_order_subjects.rq` and is **not** the VERIFIED path.
4. External dep note: `[capabilities].requires =
   urn:ggen:pack:semantic-jira-pack` — if that pack tree is absent, court is
   **BLOCKED:missing-semantic-jira-pack** (materialize script exit 2), not a
   silent PASS.

## Namespace

| Prefix | IRI |
|--------|-----|
| `ip:` | `https://ggen.dev/ontology/issue-platform-controls#` |
| `sj:` | `https://ggen-igniter.dev/ontology/semantic-jira#` |
| `dfcm:` | `https://ggen.dev/ontology/dfcm#` |

## Control classes ↔ F5

| Class | `skos:exactMatch` |
|-------|-------------------|
| `ip:Tenant` | `dfcm:F5TenantIsolation` |
| `ip:SoDConflict` | `dfcm:F5SegregationOfDuties` |
| `ip:AuditEvent` | `dfcm:F5AuditLedgerExport` |
| `ip:RetentionPolicy` | `dfcm:F5RetentionResidency` |
| `ip:AuthoritySeparation` | `dfcm:F5AuthoritySeparation` |

## Composition (with `sj:`, not instead of)

- `sj:WorkOrder ip:boundTenant ip:Tenant` — opt-in tenancy edge
- `sj:WorkOrder ip:workOrderDataClass "…"` — requires a matching retention policy
- `ip:AuditEvent ip:subjectWorkOrder sj:WorkOrder` — audit binds an order; does not redefine it
- SoD is evaluated on `ip:Principal` / `ip:Role` / `ip:conflictsWith` (and `ip:SoDConflict`)

## Gates (any row = refusal)

| Gate | Law |
|------|-----|
| `010_no_workorder_fork.rq` | No `ip:` class may `rdfs:subClassOf+ sj:WorkOrder` |
| `020_tenant_isolation.rq` | Tenant id, boundTenant typing, audit/tenant match |
| `030_sod_conflicting_roles.rq` | Conflicting role pair without exception receipt |
| `040_audit_event.rq` | Actor/action/outcome/time/integrity + WO typing |
| `050_retention_policy.rq` | Days/region/dataClass; WO data class coverage |

## Layout

- `ontology.ttl` — vocabulary + F5 bindings
- `shapes/ip.shacl.ttl` — SHACL NodeShapes (under `shapes/`; root `shapes.ttl` refused)
- `gates/*.rq` — fail-closed SPARQL twins
- `templates/010_controls_inventory.md.tera` — markdown inventory projection
- `templates/020_controls_projection.ttl.tera` — flattened TTL projection
- `qualification/consumer.ttl` — positive consumer (0-row gate court)
- `qualification/materialize_sj_dep_court.sh` — admitted SJ dep materializer
- `tests/mutations/*.ttl` — one falsifier family per gate
- `pack.toml` — identity + gate list
- `STANDING.md` — VERIFIED evidence table

Authority ceiling: NONE (SELECT/refuse + CONSTRUCT projection only).
