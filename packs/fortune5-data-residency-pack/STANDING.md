# fortune5-data-residency-pack Standing

Standing: VERIFIED

## Authored (this lane)

- `ontology.ttl` — typed residency vocabulary + catalog scaffold individuals
- `shapes/f5dr.shacl.ttl` — SHACL twin of gates 010/020 (closed provider enum,
  broker-only, forbid cross-border)
- `gates/010_residency_contract.rq`, `gates/020_broker_only_no_actuation.rq`
- `templates/residency_inventory.md.tera`, `templates/residency_contract.ttl.tera`
- `tests/mutations/{direct_actuation,cross_border_open,unsafe_provider}.ttl`

## Coordinator evidence (2026-11-19)

Source: [Validate F500 residency retention packs](6a5610b6-b48a-4530-bd23-4d30c122938b).
Binary: `ggen 26.11.5`. Courts: `uv run --no-project --with rdflib --with pyshacl`.
cwd: `packs/fortune5-data-residency-pack` (scratch sync in `mktemp -d`).

Per-pack Standing: **VERIFIED** (all EXIT=0 below). Composition remains **BLOCKED**.

| Command | EXIT | Notes |
|---|---|---|
| `ggen graph validate --files ontology.ttl --shapes shapes/f5dr.shacl.ttl` | **0** | 96 quads, `shapes_conform: true` |
| scratch frontmatter `ggen.toml` + `ggen sync run --dry-run --skip-ea-admission` | **0** | planned: `residency_inventory.md`, `residency_contract.ttl` |
| scratch `ggen sync run --skip-ea-admission` | **0** | wrote both under `infrastructure/data/transactional/` |
| rdflib clean: gates 010+020 | **0** | 0 rows each |
| pyshacl clean | **0** | `Conforms: True` |
| mutation court (3 fixtures) | **0** | 3/3 FLIP |

| Mutation | Gate flip | SHACL |
|---|---|---|
| `direct_actuation` | 020 → 1 row | Conforms: False (rc=1) |
| `cross_border_open` | 020 → 1 row | Conforms: False (rc=1) |
| `unsafe_provider` | 020 → 1 row | Conforms: False (rc=1) |

### Residuals

- Gate **010** anti-vacuity: **UNVERIFIED** — current fixtures never flip incomplete-contract
  (no incomplete mutant; fixtures target value refusals). Not a court FAIL.
- Composition: **BLOCKED** — sibling `fortune5-transaction-data-law-pack` absent
  (`test -d` rc=1). Do not invent.

## BLOCKED (missing SoT — exact reasons)

1. **Sibling commonPack absent:** catalog lists
   `fortune5-transaction-data-law-pack` beside this pack under group
   `transaction-data`, but
   `/Users/sac/ggen-marketplace/packs/fortune5-transaction-data-law-pack/`
   does not exist. Cross-pack composition court cannot run.
2. **Provider / Ash data-plane projections:** catalog
   `provider_packs` (`aws-aurora-pack`, `azure-sql-pack`, `gcp-cloud-sql-pack`,
   …) and BRCE actuation are downstream. Emitting live HCL, connection
   strings, or tenant region pins would invent secrets / customer SoT —
   refused. Law + inventory projections only.
3. **Customer residency SoT absent:** scaffold individuals
   (`RES-TXN-HOME-001`, `us-east-1`) are illustrative catalog bindings, not
   a named enterprise residency register.
