# fortune5-transaction-data-law-pack Standing

Standing: UNVERIFIED

## Authored (this lane)

- `ontology.ttl` — typed durability vocabulary + catalog scaffold individuals
- `shapes/f5td.shacl.ttl` — SHACL twin of gates 010/020
- `gates/010_durability_contract.rq`, `gates/020_broker_only_no_actuation.rq`
- `templates/txn_durability_inventory.md.tera`,
  `templates/txn_durability_contract.ttl.tera`
- `tests/mutations/{direct_actuation,pitr_disabled,catalog_id_drift}.ttl`
- Capability URN `urn:ggen:pack:fortune5-transaction-data-law-pack`

## Coordinator courts (pending)

Binary: `ggen 26.11.5`. Expected cwd:
`packs/fortune5-transaction-data-law-pack` (scratch sync in `mktemp -d`).

| Command | Expected |
|---|---|
| `ggen graph validate --files ontology.ttl --shapes shapes/f5td.shacl.ttl` | EXIT 0, shapes_conform |
| scratch dry-run / sync `--skip-ea-admission` | plan/write `txn_durability_inventory.md`, `txn_durability_contract.ttl` |
| rdflib clean: gates 010+020 | 0 rows each |
| pyshacl clean | Conforms: True |
| mutation court (3 fixtures) | 3/3 FLIP |

## BLOCKED (missing SoT — exact reasons)

1. **Coordinator sync/court not yet run** — Standing remains UNVERIFIED until
   graph validate + gate/mutation courts land evidence.
2. **Provider / Ash data-plane projections:** catalog `provider_packs`
   (`aws-aurora-pack`, `azure-sql-pack`, `gcp-cloud-sql-pack`, …) and BRCE
   actuation are downstream. Emitting live HCL, connection strings, or
   customer backup credentials would invent secrets / customer SoT —
   refused. Law + inventory projections only.
3. **Customer durability SoT absent:** scaffold individuals
   (`DUR-TXN-MZ-001`, 35-day backup) are illustrative catalog bindings, not
   a named enterprise durability register.
