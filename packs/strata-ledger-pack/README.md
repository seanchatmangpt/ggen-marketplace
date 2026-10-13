# strata-ledger-pack

Class: CapabilityPack. Profile: project. Authority: SELECT/CONSTRUCT only, no DO.

## Identity

Strata ledger state machine (roadmap slice S4,
`docs/sjira/v26.10.8/STRATA-BLOCKCHAIN-ROADMAP.md`): account-based state
transition function — credit/debit conservation, double-spend refusal via an
explicit refusal valve, overflow refusal, receipt chaining — projected as a
self-contained serde-free Rust module.

## Law provenance (REUSE-ADAPTED via ONTOLOGY PROJECTION ONLY)

Per the roadmap S5/S8 precondition outcome, the ledger law is extracted from
`/Users/sac/unibit/crates/unibit-kernel/src/lib.rs` and re-projected as strata
RDF (BUSL-1.1 + `publish = false` forbids code vendoring):

| unibit invariant | strata projection |
|---|---|
| `UDenial` zero=admitted polarity | `LedgerRefusal` — every non-admission is a typed variant; admission is only `Ok(..)` |
| `commit_masked` all-or-nothing | `apply_transition` runs every gate before any balance mutates; a refused tx leaves state bit-identical |
| `UReceipt` / `verify_receipt_chain` | `StateTransitionReceipt` + `LedgerState::verify_receipt_chain` — each receipt's `prev_root` equals the prior state root |

No unibit code is vendored; `requires = []` (FM-PACK-018).

## Capability surface

```bash
$ ggen pack capabilities strata-ledger-pack
provides: urn:ggen:pack:strata-ledger-pack, urn:strata:ledger:state-v1
requires: (none — FM-PACK-018, see pack.toml)
```

## State machine

```text
apply_transition(state, tx: &TxLike) -> Result<StateTransitionReceipt, LedgerRefusal>

gates (all run before any mutation — masked commit):
  1. Replay valve      — tx digest already applied → Replay
  2. Double-spend valve — per-account nonce must strictly advance → DoubleSpend
  3. Overflow           — checked sums on input AND output side → Overflow
  4. Conservation       — sum(inputs) == sum(outputs) → Conservation
  5. Funds/Capacity     — checked debits, MAX_ACCOUNTS cap → InsufficientFunds / CapacityExceeded

commit: debits → credits → nonce advance → digest seen-set insert
        → index += 1 → root recompute (FNV-1a placeholder mixing until S1
        binds the real hash) → receipt(prev_root, next_root, tx_digest)
```

`TxLike` is a local minimal tx shape (nonce, inputs, outputs, digest), S2-shaped
after `packs/strata-tx-pack`'s Tx by documentation-only provenance comment — no
cross-pack dependency.

## Gates

- `gates/010_ledger_layout.rq` — LEDGER_CONSTANTS presence + typed/
  malformed-integer fail-closed arms (V7 pattern). 0 rows = pass.
- `gates/020_transition_law.rq` — the projected law over the witness chain
  individuals in `ontology.ttl`: presence (prev/next root, tx digest, receipt),
  transitionIndex uniqueness, receipt mirroring, prev→next chain linearity.
  0 rows = pass. Mutation witnesses (each fires): dropped constant, untyped
  constant, malformed integer, dropped receipt link, duplicate index, broken
  chain, receipt drift.

## Verification receipts

```bash
ggen sync run ×2 → byte-identical (sha256 recorded in errc-tracker.md)
rustc --test generated/ledger_state.rs → 6 passed; 0 failed
python3 scripts/marketplace.py validate → packs=319, 0 errors
python3 scripts/qualify_packs.py --pack strata-ledger-pack → ALIVE
```

## Standing

ALIVE (exact subject: this working tree, uncommitted; qualification receipt
`/tmp/ledger-qual.json`). Generated files are consequences of `ontology.ttl`
via `ggen.toml` — repair the source, never the projection.
