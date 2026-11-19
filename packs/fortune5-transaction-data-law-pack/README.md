# fortune5-transaction-data-law-pack

Constitutional transactional-data durability law for Fortune 5. Catalog
identity matches `fortune5-deployment-blocks-pack` group `transaction-data`
`bb:commonPack` / `common_packs` entry `fortune5-transaction-data-law-pack`.

## Catalog binding

| Surface | Value |
|---|---|
| Catalog group | `transaction-data` |
| Catalog version | `26.7.31` |
| Catalog pack id | `fortune5-transaction-data-law-pack` |
| Sibling common pack | `fortune5-data-residency-pack` |
| Provider packs (downstream) | `aws-aurora-pack`, `aws-dynamodb-global-tables-pack`, `azure-sql-pack`, `azure-cosmos-db-pack`, `gcp-cloud-sql-pack`, `gcp-spanner-pack` |
| Output directory (group) | `infrastructure/data/transactional` |

## Law

A durability program must pin:

- multi-zone placement (`multiZoneRequired true`);
- encryption at rest;
- automated backups with positive `backupRetentionDays`;
- point-in-time recovery (`pitrEnabled true`);
- a named replication policy (`sync` / `async` only);
- evidence required for any durability claim;
- `directActuation false` (broker-only; BRCE is the actuation boundary);
- `catalogPackId "fortune5-transaction-data-law-pack"` for catalog equivalence.

## Gates / SHACL

| Gate | Refusal |
|---|---|
| `gates/010_durability_contract.rq` | Incomplete program, policy, or replication contract |
| `gates/020_broker_only_no_actuation.rq` | Direct actuation, disabled durability controls, unsafe replication mode, or catalog-id drift |
| `shapes/f5td.shacl.ttl` | SHACL twin of the above (manual `ggen graph validate`) |

## Templates

| Template | Output |
|---|---|
| `templates/txn_durability_inventory.md.tera` | `infrastructure/data/transactional/txn_durability_inventory.md` |
| `templates/txn_durability_contract.ttl.tera` | `infrastructure/data/transactional/txn_durability_contract.ttl` |

## Standing

See `STANDING.md`. Authored SHACL/TTL/templates are real; standing remains
**UNVERIFIED** until coordinator sync/court. Provider HCL and Ash data-plane
are **BLOCKED** on missing SoT (no secrets invented).
