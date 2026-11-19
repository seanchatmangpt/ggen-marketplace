# fortune5-object-storage-law-pack Standing

Standing: VERIFIED

## Authored (this lane)

- `ontology.ttl` — typed object-storage vocabulary + catalog scaffold individuals
- `shapes/f5os.shacl.ttl` — SHACL twin of gates 010/020
- `gates/010_storage_contract.rq`, `gates/020_broker_only_no_actuation.rq`
- `templates/object_storage_inventory.md.tera`,
  `templates/object_storage_contract.ttl.tera`
- `tests/mutations/{direct_actuation,versioning_disabled,catalog_id_drift}.ttl`
- Capability URN `urn:ggen:pack:fortune5-object-storage-law-pack`

## Coordinator evidence (2026-11-19)

Source: [Validate F500 sibling packs](8b09808e-d967-4b32-a28c-27547b14961d).
Binary: `ggen 26.11.5`. Courts: `uv run --no-project --with rdflib --with pyshacl`.
cwd: `packs/fortune5-object-storage-law-pack` (scratch sync in `mktemp -d`).

Per-pack Standing: **VERIFIED** (all EXIT=0 below). Composition SoT remains **BLOCKED**.

| Command | EXIT | Notes |
|---|---|---|
| `ggen graph validate --files ontology.ttl --shapes shapes/f5os.shacl.ttl` | **0** | 97 quads, `shapes_conform: true` |
| scratch dry-run `--skip-ea-admission` | **0** | planned: `object_storage_inventory.md`, `object_storage_contract.ttl` |
| scratch sync `--skip-ea-admission` | **0** | wrote both under `infrastructure/data/object-storage/` |
| rdflib clean: gates 010+020 | **0** | 0 rows each |
| pyshacl clean | **0** | `Conforms: True` |
| mutation court (3 fixtures) | **0** | 3/3 FLIP |

| Mutation | Gate flip | SHACL |
|---|---|---|
| `direct_actuation` | 020 → 1 row | Conforms: False (rc=1) |
| `versioning_disabled` | 020 → 1 row | Conforms: False (rc=1) |
| `catalog_id_drift` | 020 → 1 row | Conforms: False (rc=1) |

### Residuals

- Gate **010** anti-vacuity: **UNVERIFIED** — current fixtures never flip incomplete-contract
  (all flips are 020 only). Not a court FAIL; do not claim Gate 010 VERIFIED.

## BLOCKED (missing SoT — exact reasons)

1. **Provider / Ash / WORM data-plane projections:** catalog `provider_packs`
   (`aws-s3-pack`, `aws-s3-object-lock-pack`, `azure-immutable-blob-pack`,
   `gcp-bucket-lock-pack`, …) and Smalt Blob WORM faces are downstream
   actuation SoT. Emitting live bucket policies, immutability tokens, or
   access keys would invent secrets / customer SoT — refused. Law +
   inventory projections only.
2. **Customer bucket SoT absent:** scaffold individuals
   (`BUCKET-EVIDENCE-001`, LC 90/2555) are illustrative catalog bindings,
   not a named enterprise object-storage register.
