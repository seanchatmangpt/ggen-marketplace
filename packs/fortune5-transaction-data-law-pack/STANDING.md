# fortune5-transaction-data-law-pack Standing

Standing: VERIFIED

## Authored (this lane)

- `ontology.ttl` — typed durability vocabulary + catalog scaffold individuals
- `shapes/f5td.shacl.ttl` — SHACL twin of gates 010/020
- `gates/010_durability_contract.rq`, `gates/020_broker_only_no_actuation.rq`
- `templates/txn_durability_inventory.md.tera`,
  `templates/txn_durability_contract.ttl.tera`
- `tests/mutations/{direct_actuation,pitr_disabled,catalog_id_drift}.ttl`
- Capability URN `urn:ggen:pack:fortune5-transaction-data-law-pack`

## Coordinator evidence (2026-11-19)

Source: [Validate F500 sibling packs](8b09808e-d967-4b32-a28c-27547b14961d).
Binary: `ggen 26.11.5`. Courts: `uv run --no-project --with rdflib --with pyshacl`.
cwd: `packs/fortune5-transaction-data-law-pack` (scratch sync in `mktemp -d`).

Per-pack Standing: **VERIFIED** (all EXIT=0 below). Composition SoT remains **BLOCKED**.

| Command | EXIT | Notes |
|---|---|---|
| `ggen graph validate --files ontology.ttl --shapes shapes/f5td.shacl.ttl` | **0** | 103 quads, `shapes_conform: true` |
| scratch dry-run `--skip-ea-admission` | **0** | planned: `txn_durability_inventory.md`, `txn_durability_contract.ttl` |
| scratch sync `--skip-ea-admission` | **0** | wrote both under `infrastructure/data/transactional/` |
| rdflib clean: gates 010+020 | **0** | 0 rows each |
| pyshacl clean | **0** | `Conforms: True` |
| mutation court (3 fixtures) | **0** | 3/3 FLIP |

| Mutation | Gate flip | SHACL |
|---|---|---|
| `direct_actuation` | 020 → 1 row | Conforms: False (rc=1) |
| `pitr_disabled` | 020 → 1 row | Conforms: False (rc=1) |
| `catalog_id_drift` | 020 → 1 row | Conforms: False (rc=1) |

### Residuals

- Gate **010** anti-vacuity: **UNVERIFIED** — current fixtures never flip incomplete-contract
  (all flips are 020 only). Not a court FAIL; do not claim Gate 010 VERIFIED.

## BLOCKED (missing SoT — exact reasons)

1. **Provider / Ash data-plane projections:** catalog `provider_packs`
   (`aws-aurora-pack`, `azure-sql-pack`, `gcp-cloud-sql-pack`, …) and BRCE
   actuation are downstream. Emitting live HCL, connection strings, or
   customer backup credentials would invent secrets / customer SoT —
   refused. Law + inventory projections only.
2. **Customer durability SoT absent:** scaffold individuals
   (`DUR-TXN-MZ-001`, 35-day backup) are illustrative catalog bindings, not
   a named enterprise durability register.

## Lane 07 re-court (2026-11-19, v26.11.19)

Binary `ggen 26.11.5`. validate + scratch sync + rdflib clean + mutation FLIP all EXIT=0. Gate **010** anti-vacuity residual remains **UNVERIFIED** (fixtures do not flip incomplete-contract).
Standing: **VERIFIED**.
