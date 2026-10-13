# errc-tracker.md — strata-store-pack hardening wave 2026-10-13

ERRC pass; citations re-verified at write time.

## Eliminate

No dead surface: pack created this session (roadmap slice S6, GREENFIELD);
nothing to retire. The trait's infallible `put` deliberately does NOT carry
the capacity refusal (it would require panicking or changing the roadmap
trait shape); the typed valve lives on `try_put` — a refused capacity put via
`put` is observable through `len`/`contains` and the typed surface is
`try_put`.

## Reduce

One shared query (`queries/store_constants.rq`) feeds both generation rules
(store-consts, store-engine), so constants have exactly one RDF source — no
second literal table in the engine template.

## Raise

- Fail-closed gates: `gates/010_store_layout.rq` (presence + V7
  datatype/malformed-integer arms + capacity > 0) and
  `gates/020_store_closure.rq` (exact property set, presence arms,
  receipt-mirror) — any violation row fails sync/verify.
- Receipt-mirror law in gate 020: a `StoreReceipt` whose
  `receiptRootDigest` matches no `ContentStore` `rootDigest` fires —
  a receipt for a state that was never observed is a violation.
- 10 generated Rust courts (all passing): round-trip ×100, dedup,
  rollback restore, rollback-past-genesis refusal, capacity bound refusal,
  content-derived keys, marker ordering, root-digest tracking, deduped-put
  journaling, FIPS 180-4 SHA-256 vectors.
- Witness individuals (`so:store-witness`, `so:entry-a/b`,
  `so:receipt-witness`) keep gate 020 non-vacuous — the law is exercised
  over real rows, never over an empty class.

## Create

Pending roadmap slices build on the `ContentStore` trait surface
(`urn:strata:store:v1`); the crash-consistency courts called for by S6 are
the root-digest + receipt-mirror gate arms plus the generated rollback
courts; persistent backends (rocksdb/sled trait implementations) remain
future work by roadmap design.
