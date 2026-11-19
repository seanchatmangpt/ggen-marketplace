# fortune5-data-residency-pack

Constitutional data-residency law for Fortune 5 transactional data. Catalog
identity matches `fortune5-deployment-blocks-pack` group `transaction-data`
`bb:commonPack` / `common_packs` entry `fortune5-data-residency-pack`.

## Catalog binding

| Surface | Value |
|---|---|
| Catalog group | `transaction-data` |
| Catalog version | `26.7.31` |
| Sibling common pack | `fortune5-transaction-data-law-pack` (**directory absent** — composition BLOCKED) |
| Provider packs (downstream) | `aws-aurora-pack`, `aws-dynamodb-global-tables-pack`, `azure-sql-pack`, `azure-cosmos-db-pack`, `gcp-cloud-sql-pack`, `gcp-spanner-pack` |
| Output directory (group) | `infrastructure/data/transactional` |

## Law

A residency program must pin:

- home and allowed jurisdictions;
- provider region pins (`aws` / `azure` / `gcp` only);
- `forbidCrossBorderReplication true`;
- evidence required for any residency claim;
- `directActuation false` (broker-only; BRCE is the actuation boundary).

## Gates / SHACL

| Gate | Refusal |
|---|---|
| `gates/010_residency_contract.rq` | Incomplete program or policy contract |
| `gates/020_broker_only_no_actuation.rq` | Direct actuation, open cross-border replication, or non-catalog provider |
| `shapes/f5dr.shacl.ttl` | SHACL twin of the above (manual `ggen graph validate`) |

## Templates

| Template | Output |
|---|---|
| `templates/residency_inventory.md.tera` | `infrastructure/data/transactional/residency_inventory.md` |
| `templates/residency_contract.ttl.tera` | `infrastructure/data/transactional/residency_contract.ttl` |

## Standing

See `STANDING.md`. Authored SHACL/TTL/templates are real; standing remains
**UNVERIFIED** until coordinator sync/court. Provider HCL and Ash data-plane
are **BLOCKED** on missing SoT (no secrets invented).
