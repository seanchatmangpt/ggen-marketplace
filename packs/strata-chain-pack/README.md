# strata-chain-pack

S5 of the Strata blockchain roadmap
(`docs/sjira/v26.10.8/STRATA-BLOCKCHAIN-ROADMAP.md`): the block + chain
layer as an ontology-backed ggen pack. Projects the genesis constants and a
self-contained chain engine — block header with parent-hash chaining over
Merkle tx commits, the chain-validity law (height continuity, parent-hash
binding, tx cap, duplicate-tx refusal, Merkle commitment, monotonic
timestamp slot, PoW re-check), deterministic PoW mining, and deterministic
fork choice — generation over hand-writing per doctrine.

## What it projects

Two generated Rust modules from one RDF ontology
(`https://strata.chatman.ai/ontology#`):

- `generated/chain_consts.rs` — `GENESIS_HEIGHT`, `MAX_BLOCK_TXS`,
  `INITIAL_DIFFICULTY_TARGET`, `GENESIS_PREV` (32-byte all-zero parent
  hash), `DIGEST_LEN`.
- `generated/chain_engine.rs` — zero-crate SHA-256 (FIPS 180-4, provenance-
  copied strata-hash-pack pattern with the FIPS test vectors), Merkle tx
  commitment (single SHA-256 per level, duplicate-last odd rule; empty tx
  set commits to SHA-256 of the empty string), the `Block` model,
  `validate_block(parent, block) -> Result<(), ChainRefusal>` (typed
  refusals: `HeightContinuity`, `ParentHashMismatch`, `TxCapExceeded`,
  `DuplicateTx`, `MerkleRootMismatch`, `SlotRegression`,
  `PoWTargetNotMet`), `mine_tick` (deterministic PoW nonce search —
  leading-zero-bits target, no RNG, no wall-clock), `attach`,
  `fork_choice` (longest valid chain wins; equal-height tie → lower tip
  nonce), and `reorg` (returns the displaced blocks when a candidate wins).

## Build

```bash
cd packs/strata-chain-pack
ggen sync run    # regenerates generated/*.rs from ontology.ttl
rustc --test -O generated/chain_engine.rs -o /tmp/chain_engine && /tmp/chain_engine
rustc --test generated/chain_consts.rs -o /tmp/chain_consts && /tmp/chain_consts
```

## Verification ladder (receipted this session)

1. `ggen sync run` x2 → byte-identical outputs (chain_consts
   `cd8f90e4…`, chain_engine `a2a9e88c…`).
2. `rustc --test` — 14/14 tests pass in `chain_engine.rs`
   (FIPS vectors, genesis shape, chain-of-five, parent-hash/height-gap/
   merkle-tamper/dup-tx/tx-cap/slot-regression refusals, fork choice,
   fork tie → lower nonce, reorg displaced blocks, PoW determinism).
3. Gates zero-rows via rdflib (010 block-layout presence + typed/
   malformed arms; 020 chain law over the REAL witness chain
   genesis → B1 → B2 with a documented fork sibling).
4. `python3 scripts/marketplace.py validate` — 321 packs validated,
   exit 0.
5. `scripts/qualify_packs.py --pack`/full run — `strata-chain-pack`
   status **ALIVE**.

## Law provenance

S5 REUSE-ADAPTED for the gate law, greenfield for header/chain logic, per
the roadmap S5/S8 precondition outcome. Merkle/SHA-256 conventions are
provenance-copied PATTERNS from `strata-hash-pack` ground truth (FIPS
180-4); no BUSL-1.1 code vendored; no `owl:imports` (FM-PACK-018 note in
`pack.toml`).
