# fortune5-object-storage-law-pack

Constitutional object and evidence storage law for Fortune 5. Catalog
identity matches `fortune5-deployment-blocks-pack` group `object-storage`
`bb:commonPack` / `common_packs` entry `fortune5-object-storage-law-pack`.

## Catalog binding

| Surface | Value |
|---|---|
| Catalog group | `object-storage` |
| Catalog version | `26.7.31` |
| Catalog pack id | `fortune5-object-storage-law-pack` |
| Sibling common pack | `fortune5-retention-pack` (dir `fortune5-retention-legal-hold-pack`) |
| Provider packs (downstream) | `aws-s3-pack`, `aws-s3-object-lock-pack`, `azure-blob-storage-pack`, `azure-immutable-blob-pack`, `gcp-cloud-storage-pack`, `gcp-bucket-lock-pack` |
| Output directory (group) | `infrastructure/data/object-storage` |

## Law

An object-storage program must pin:

- versioning enabled;
- encryption at rest;
- immutable-capable posture for evidence classes;
- at least one lifecycle rule with positive `transitionDays` and
  `expireDays` (`expireDays >= transitionDays`);
- evidence required for any storage claim;
- `directActuation false` (broker-only; BRCE is the actuation boundary);
- `catalogPackId "fortune5-object-storage-law-pack"` for catalog equivalence.

## Gates / SHACL

| Gate | Refusal |
|---|---|
| `gates/010_storage_contract.rq` | Incomplete program, bucket law, or lifecycle contract |
| `gates/020_broker_only_no_actuation.rq` | Direct actuation, disabled storage controls, non-positive lifecycle days, or catalog-id drift |
| `shapes/f5os.shacl.ttl` | SHACL twin of the above (manual `ggen graph validate`) |

## Templates

| Template | Output |
|---|---|
| `templates/object_storage_inventory.md.tera` | `infrastructure/data/object-storage/object_storage_inventory.md` |
| `templates/object_storage_contract.ttl.tera` | `infrastructure/data/object-storage/object_storage_contract.ttl` |

## Standing

See `STANDING.md`. Authored SHACL/TTL/templates are real; standing remains
**UNVERIFIED** until coordinator sync/court. Provider WORM/Ash projections
are **BLOCKED** on missing SoT (no secrets invented).
