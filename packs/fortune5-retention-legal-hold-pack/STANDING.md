# fortune5-retention-legal-hold-pack Standing

Standing: VERIFIED

## Authored (this lane)

- `ontology.ttl` — typed retention/hold vocabulary + catalog scaffold individuals
- `shapes/f5rh.shacl.ttl` — SHACL twin of gates 010/020/030
- `gates/010_retention_contract.rq`, `gates/020_legal_hold_blocks_delete.rq`,
  `gates/030_broker_only_no_actuation.rq`
- `templates/retention_inventory.md.tera`, `templates/retention_contract.ttl.tera`
- `tests/mutations/{hold_allows_delete,nonpositive_retention,catalog_id_drift}.ttl`
- Capability URNs include catalog id `urn:ggen:pack:fortune5-retention-pack`

## Coordinator evidence (2026-11-19)

Source: [Validate F500 residency retention packs](6a5610b6-b48a-4530-bd23-4d30c122938b).
Binary: `ggen 26.11.5`. Courts: `uv run --no-project --with rdflib --with pyshacl`.
cwd: `packs/fortune5-retention-legal-hold-pack` (scratch sync in `mktemp -d`).

Per-pack Standing: **VERIFIED** (all EXIT=0 below). Composition remains **BLOCKED**.

| Command | EXIT | Notes |
|---|---|---|
| `ggen graph validate --files ontology.ttl --shapes shapes/f5rh.shacl.ttl` | **0** | 108 quads, `shapes_conform: true` |
| scratch dry-run `--skip-ea-admission` | **0** | planned: `retention_inventory.md`, `retention_contract.ttl` |
| scratch sync `--skip-ea-admission` | **0** | wrote both under `infrastructure/data/object-storage/` |
| rdflib clean: gates 010+020+030 | **0** | 0 rows each |
| pyshacl clean | **0** | `Conforms: True` |
| mutation court (3 fixtures) | **0** | 3/3 FLIP |

| Mutation | Gate flip | SHACL |
|---|---|---|
| `hold_allows_delete` | 020 → 1 row | Conforms: False (rc=1) |
| `nonpositive_retention` | 030 → 1 row | Conforms: False (rc=1) |
| `catalog_id_drift` | 030 → 1 row | Conforms: False (rc=1) |

### Residuals

- Gate **010** anti-vacuity: **UNVERIFIED** — current fixtures never flip incomplete-contract
  (no incomplete mutant; fixtures target value refusals). Not a court FAIL.
- Composition: **BLOCKED** — sibling `fortune5-object-storage-law-pack` absent
  (`test -d` rc=1). Do not invent.

## BLOCKED (missing SoT — exact reasons)

1. **Sibling commonPack absent:** catalog lists
   `fortune5-object-storage-law-pack` beside `fortune5-retention-pack` under
   group `object-storage`, but
   `/Users/sac/ggen-marketplace/packs/fortune5-object-storage-law-pack/`
   does not exist. Cross-pack composition court cannot run.
2. **Provider / Ash / WORM data-plane projections:** catalog
   `provider_packs` (`aws-s3-object-lock-pack`, `azure-immutable-blob-pack`,
   `gcp-bucket-lock-pack`, …) and Smalt Blob WORM faces are downstream
   actuation SoT. Emitting live bucket policies, immutability tokens, or
   sealed matter payloads would invent secrets / legal SoT — refused.
   Law + inventory projections only. Related emulator:
   `industry-legal-ediscovery` (not this catalog id).
3. **Customer matter/hold SoT absent:** scaffold
   (`HOLD-MATTER-001`, `obj-receipt-ledger-001`, 2555-day schedule) is
   illustrative catalog binding, not a named enterprise legal-hold register.

## Lane 07 re-court (2026-11-19, v26.11.19)

Binary `ggen 26.11.5`. validate + scratch sync + rdflib clean + mutation FLIP all EXIT=0. Gate **010** anti-vacuity residual remains **UNVERIFIED** (fixtures do not flip incomplete-contract).
Standing: **VERIFIED**.
