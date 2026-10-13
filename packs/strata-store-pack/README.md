# strata-store-pack

Class: CapabilityPack. Profile: project. Authority: SELECT/CONSTRUCT only, no DO.

## Identity

Content-addressed storage for Strata (roadmap slice S6,
`docs/sjira/v26.10.8/STRATA-BLOCKCHAIN-ROADMAP.md` — GREENFIELD: no storage
code existed to reuse). Projects a `ContentStore` trait
(put/get/contains/len/mark/rollback_to/root_digest) with an in-memory
capacity-bounded impl keyed by inline SHA-256, plus typed refusals
(`StoreRefusal::CapacityExhausted`, `RollbackPastGenesis`).

## Capability surface

```bash
$ ggen pack capabilities strata-store-pack
```

## Storage layer (S6)

`generated/store_engine.rs` (rule `store-engine`) is self-contained and
compiles standalone via `rustc --test`:

- **Content addressing** — `put(value)` keys by SHA-256(value); identical
  values dedup to one entry and never grow the store.
- **Marker rollback (re-org rollback)** — `mark()` records the journal
  length; `rollback_to` removes exactly the keys inserted after the marker
  (append-only store, tombstone-free rollback). Deduped puts do not journal,
  so a rollback never removes a pre-marker original. Rollback past genesis
  is a typed `StoreRefusal::RollbackPastGenesis`.
- **Atomic reorg undo (`undo_to_fork`)** — undoes ALL post-fork entries in
  ONE operation and returns a single `StoreReceipt` (operation, fork
  marker, entries undone, post root digest). Crash-safe by write-ahead
  recovery: the RECOVERY record is written BEFORE any deletion, so an undo
  interrupted mid-deletion replays to completion via
  `recover_interrupted_undo()` — the store is never left in an admissible
  partial state. A new undo while one is pending recovery refuses typed
  (`StoreRefusal::UndoInterruptedPending`). Courts: deep reorg (100
  entries) with mid-undo crash at every crash point ×100 iterations,
  each recovering exactly to the fork-point root digest.
- **Capacity valve** — `try_put` returns
  `StoreRefusal::CapacityExhausted` at the bound
  (`DEFAULT_CAPACITY` = 1_048_576, projected from `so:STORE_CONSTANTS`);
  a refused put never grows the store.
- **Root digest** — `root_digest()` is SHA-256 over the concatenated
  in-order keys (`st:rootDigest` — the crash-consistency court surface).

The SHA-256 in `store_engine.rs` is an inline provenance copy of
strata-hash-pack's generated primitive (cross-pack consumption of a
per-pack-generated module would couple two generated artifacts; self-contained
wins — the S3 remediation, reused).

## Evidence boundary

Marketplace admission and ggen qualification of this bounded boundary only.
The in-memory store is not a qualified persistent storage engine
(rocksdb/sled backends are a later roadmap slice); qualification proves the
generated module's behavior on the exact synced subject, nothing more.
