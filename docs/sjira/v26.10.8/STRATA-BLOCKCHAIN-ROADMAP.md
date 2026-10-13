# STRATA Blockchain Capability Roadmap — Work Order (CLOSED 2026-10-13)

All ten slices S1–S10 landed; closure receipt:
`docs/sjira/v26.10.8/STRATA-BLOCKCHAIN-CLOSE.md`. Slice table retained below
as the original dependency-ordered work order.

- **Directive** (operator, 2026-10-13): loop cron drives incremental feature
  slices toward full blockchain capability. Each slice: new pack(s) or pack
  extensions in dependency order, RDF-source + generation + gates + tests +
  receipts per house doctrine, court-verified before merge.
- **Honest baseline**: strata is a court-verified specification substrate
  (wire constants, refusal taxonomy, attestation sizes, admission valves,
  Petri-net transition ABI). No consensus, network, or execution exists.
  This roadmap builds those, slice by slice, each slice independently
  verifiable.

## Slices (dependency order; one per loop iteration, court-gated)

| # | Slice | New/extended packs | Deliverable | Verification bar |
|---|---|---|---|---|
| S1 | Crypto primitives | `strata-hash-pack` (BLAKE3/SHA-256 consts + Merkle tree impl, property tests) | hashing + Merkle root/proof with fuzz tests | cargo test + property courts; gates: digest-length closure |
| S2 | Transaction model | `strata-tx-pack` | Tx framing over CLAP-PDU (inputs/outputs/signature placeholder), serde round-trip, replay-guard fields | round-trip + negative-witness courts |
| S3 | Signing integration | extend `strata-signer-pack` | real ML-DSA-65 sign/verify over tx digests (bind to ~/strata signer.rs ground truth) | sign/verify positive+negative courts |
| S4 | Ledger state machine | `strata-ledger-pack` | UTXO-or-account state transition fn (reuse PN64 transition formalism as the state law), double-spend refusal via valve | state-transition property courts; valve refusal integration |
| S5 | Block + chain validation | `strata-chain-pack` | block header (extends PDU header), parent-hash chaining via cas Merkle commits, chain-validity gate incl. difficulty/height rules | chain-reorg negative courts; abutment reuse |
| S6 | Storage | `strata-store-pack` | content-addressed block/tx store (rocksdb or sled trait + in-memory impl), re-org rollback | crash-consistency courts |
| S7 | P2P wire + mempool | `strata-net-pack` | CLAP-PDU message framing for inv/getdata/tx/block gossip, mempool admission via valve | protocol conformance courts (TCK-style) |
| S8 | Consensus kernel | `strata-consensus-pack` | PoW nonce search + heaviest-chain fork choice (formalized as PN64 transition lattice) | fork-choice property courts; adversarial fork sims |
| S9 | Network hardening | extend net+valve | eclipse/spam/invalid-block refusal paths, rate limits | adversarial corpus courts |
| S10 | External audit surface | all | fuzzing (cargo-fuzz), known-attack corpus, independent review receipt | fuzz-clean + corpus-clean courts |

## Non-goals (per slice)
No token/economics claims; no mainnet pretensions; every slice carries the
Authority: SELECT/CONSTRUCT fence — packs project code, never grant DO.

## Closure definition ("full blockchain")
S1–S8 landed + S9 adversarial-clean + S10 audit receipt: a node that
validates, stores, and gossips blocks with PoW consensus — still a
reference implementation, explicitly not a production network.

## S5/S8 precondition outcome — unibit/universe-chain reuse evaluation (2026-10-13)

Evaluated `/Users/sac/unibit` (30-crate BUSL-1.1 workspace, no_std kernel,
50 tests — genuine admission/commit/receipt-chaining LAW, but bit-level
primitives, not blockchain) and `/Users/sac/universe-chain` (198-line
uncommitted sketch with a vacuous admission gate — do not build on it).

Verdicts: **S2/S4 REUSE-ADAPTED via ontology projection only** — extract the
invariants (zero-denial-admitted polarity, masked commit law, receipt
chaining) into strata RDF and regenerate; BUSL-1.1 + `publish = false`
forbids code vendoring. **S5 REUSE-ADAPTED for the gate law, greenfield for
header/chain logic. S6, S8 GREENFIELD** (no storage, nonce, difficulty, or
fork-choice code exists anywhere; `unibit-l1` "TruthBlock" is a memory
region, not a blockchain block — name-collision hazard to document).

Integration story: fresh ontology projection FROM unibit's small `Copy`
types; path-dep code reuse only as an unlicensed dev-reference if at all.
