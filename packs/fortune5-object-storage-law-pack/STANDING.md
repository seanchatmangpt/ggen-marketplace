# fortune5-object-storage-law-pack Standing

Standing: UNVERIFIED

## Authored (this lane)

- `ontology.ttl` — typed object-storage vocabulary + catalog scaffold individuals
- `shapes/f5os.shacl.ttl` — SHACL twin of gates 010/020
- `gates/010_storage_contract.rq`, `gates/020_broker_only_no_actuation.rq`
- `templates/object_storage_inventory.md.tera`,
  `templates/object_storage_contract.ttl.tera`
- `tests/mutations/{direct_actuation,versioning_disabled,catalog_id_drift}.ttl`
- Capability URN `urn:ggen:pack:fortune5-object-storage-law-pack`

## Coordinator courts (pending)

Binary: `ggen 26.11.5`. Expected cwd:
`packs/fortune5-object-storage-law-pack` (scratch sync in `mktemp -d`).

| Command | Expected |
|---|---|
| `ggen graph validate --files ontology.ttl --shapes shapes/f5os.shacl.ttl` | EXIT 0, shapes_conform |
| scratch dry-run / sync `--skip-ea-admission` | plan/write `object_storage_inventory.md`, `object_storage_contract.ttl` |
| rdflib clean: gates 010+020 | 0 rows each |
| pyshacl clean | Conforms: True |
| mutation court (3 fixtures) | 3/3 FLIP |

## BLOCKED (missing SoT — exact reasons)

1. **Coordinator sync/court not yet run** — Standing remains UNVERIFIED until
   graph validate + gate/mutation courts land evidence.
2. **Provider / Ash / WORM data-plane projections:** catalog `provider_packs`
   (`aws-s3-pack`, `aws-s3-object-lock-pack`, `azure-immutable-blob-pack`,
   `gcp-bucket-lock-pack`, …) and Smalt Blob WORM faces are downstream
   actuation SoT. Emitting live bucket policies, immutability tokens, or
   access keys would invent secrets / customer SoT — refused. Law +
   inventory projections only.
3. **Customer bucket SoT absent:** scaffold individuals
   (`BUCKET-EVIDENCE-001`, LC 90/2555) are illustrative catalog bindings,
   not a named enterprise object-storage register.
