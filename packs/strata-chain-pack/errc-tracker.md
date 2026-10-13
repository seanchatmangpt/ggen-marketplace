# errc-tracker.md — strata-chain-pack S5 construction lane

ERRC pass over the S5 construction. Claims verified against the working
tree at edit time (2026-10-13 session).

## Eliminate

- **No wall-clock anywhere.** `timestampSlot` is a monotonic logical slot
  (determinism law); `SlotRegression` refuses a child below its parent's
  slot. No time source, no RNG in the generated module.
- **No cross-pack require.** `requires = []` with the FM-PACK-018
  documentation-only note — the qualification capsule can never resolve a
  cross-pack dependency (same remediation as S2/S4).

## Reduce

- **One query, two rules**: `queries/chain_constants.rq` is shared by
  chain-consts and chain-engine; no duplicate query text.
- **Fork law reduces to tip comparison**: `fork_choice` and `reorg`
  compare only (tip height, tip nonce); displaced blocks are computed by
  actual shared-prefix comparison, not index arithmetic.
- **`blocks_equal` is plain `Block` equality** — kept as a named fn only
  to carry the fork-identity comment; no re-derived encoding.

## Raise

- **Typed `ChainRefusal` enum** with seven named variants carrying
  expected/got payloads — every rejection is data, never a bool.
- **Fail-closed V7 gates both directions**: 010 has presence arms AND
  typed/malformed-integer arms; 020 has five presence arms plus the
  height-continuity and duplicate-height-at-same-parent laws, exercised
  over a REAL witness chain (genesis → B1 → B2), never an empty class.
- **Determinism pinned by test**: `pow_determinism` proves same seed ⇒
  same nonce; `fork_tie_lower_nonce_wins` proves the equal-height
  tiebreak; the reorg test needed distinct txs per chain precisely
  BECAUSE mining is deterministic (identical inputs are the same chain —
  caught and fixed this session).
- **K-table provenance**: the SHA-256 round constants were spliced into
  the template programmatically from `strata-hash-pack/generated/
  hash_merkle.rs` ground truth and re-diffed (64/64 exact match) after an
  initial hand-recall produced a wrong table that the FIPS vectors would
  have caught at first run.

## Create

- **Height-2 fork sibling in the ontology** documents the tiebreak law
  while carrying deliberately NO `st:parent` link: a duplicate
  (parent, height) pair is a gate-020 violation by definition, so the
  sibling may not claim one; the tie law lives non-vacuously in the
  generated tests instead.
