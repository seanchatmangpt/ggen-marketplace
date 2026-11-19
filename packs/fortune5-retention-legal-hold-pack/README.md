# fortune5-retention-legal-hold-pack

Constitutional retention and legal-hold law for Fortune 5 object and evidence
storage. Directory and pack name expand the catalog identity; capabilities
also provide `urn:ggen:pack:fortune5-retention-pack` so the
`fortune5-deployment-blocks-pack` object-storage `bb:commonPack` /
`common_packs` entry resolves.

## Catalog binding

| Surface | Value |
|---|---|
| Catalog group | `object-storage` |
| Catalog version | `26.7.31` |
| Catalog pack id | `fortune5-retention-pack` |
| Pack directory | `fortune5-retention-legal-hold-pack` |
| Sibling common pack | `fortune5-object-storage-law-pack` (**directory absent** — composition BLOCKED) |
| Provider packs (downstream) | `aws-s3-pack`, `aws-s3-object-lock-pack`, `azure-blob-storage-pack`, `azure-immutable-blob-pack`, `gcp-cloud-storage-pack`, `gcp-bucket-lock-pack` |
| Output directory (group) | `infrastructure/data/object-storage` |

## Law

A retention program must declare:

- at least one retention schedule with positive `retentionDays` and
  `immutableCapable`;
- at least one legal hold that names a matter and held object;
- `blocksDelete true` and `blocksExport true` on every hold;
- evidence required for schedules and holds;
- `directActuation false` (broker-only; BRCE is the actuation boundary);
- `catalogPackId "fortune5-retention-pack"` for catalog equivalence.

## Gates / SHACL

| Gate | Refusal |
|---|---|
| `gates/010_retention_contract.rq` | Incomplete program or schedule contract |
| `gates/020_legal_hold_blocks_delete.rq` | Incomplete hold or hold that does not block delete/export |
| `gates/030_broker_only_no_actuation.rq` | Direct actuation, non-positive retention, or catalog-id drift |
| `shapes/f5rh.shacl.ttl` | SHACL twin of the above (manual `ggen graph validate`) |

## Templates

| Template | Output |
|---|---|
| `templates/retention_inventory.md.tera` | `infrastructure/data/object-storage/retention_inventory.md` |
| `templates/retention_contract.ttl.tera` | `infrastructure/data/object-storage/retention_contract.ttl` |

## Standing

See `STANDING.md`. Authored SHACL/TTL/templates are real; standing remains
**UNVERIFIED** until coordinator sync/court. Provider WORM/Ash projections are
**BLOCKED** on missing SoT (no secrets invented).
