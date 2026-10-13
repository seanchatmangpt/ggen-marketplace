# Reference: Strata family contracts

Exact contracts for the sixteen Strata packs (7 original + 9 blockchain/
governance/audit slices S1-S10). Two packs declare `status = "alpha"` in
`pack.toml` (`strata-protocol-pack`, `strata-valve-pack`); the other fourteen
carry no status field (version 0.1.0). All sixteen ship committed `witness.ttl`
+ `verify.py`. Values below are projected from the pack ontologies except where
noted as comment-level; the ontology is canonical. See
[../explanation/strata-family-design.md](../explanation/strata-family-design.md)
for rationale and
[../explanation/level5-diataxis.md](../explanation/level5-diataxis.md) for the
shared Diátaxis maturity doctrine this family's docs follow.

## Pack table

| Pack | Slice | Status | Output language | Law surface | Court set |
|---|---|---|---|---|---|
| `strata-protocol-pack` | core | alpha | Rust | PDU frame constants (`pdu-constants`) and wire classes (`wire-constants` → `generated/wire_constants.rs`) | 3 gates; 1 sabotage twin |
| `strata-cas-pack` | core | — | Rust | Merkle commit / wormhole / snapshot frames over CLAP-PDU types | 2 gates; 2 sabotage twins |
| `strata-pn64-pack` | core | — | Rust | PN64/OCEL64 dual-word ABI; PRE/POST mask tables (`pn64_masks`) | 3 gates; 1 sabotage twin |
| `strata-signer-pack` | core | — | Rust | ML-DSA-65 attestation constants; digest-domain tag binds tx payloads (S3) | 2 gates; 1 sabotage twin; cross-pack ML-DSA byte-flip court |
| `strata-stratus-pack` | core | — | Rust | Witness valves + state registers | 1 gate; no twin on disk |
| `strata-temprun-pack` | core | — | Rust | Fuel-lease arena table (`arena.rs`) | 1 gate; 1 sabotage twin |
| `strata-valve-pack` | core | alpha | Elixir | Refusal taxonomy atoms + `WindowCapacityRefusal` (k=8) + adversarial mirrors | 4 gates on disk (3 wired in `ggen.toml`); 1 sabotage twin |
| `strata-hash-pack` | S1 | — | Rust | SHA-256 (FIPS 180-4) + Merkle over 32-byte digests; `ChainRuleV2Fold` law; KAT court in template test module | 2 gates; 1 sabotage twin |
| `strata-tx-pack` | S2 | — | Rust | Tx header framing + replay-guard nonce; BLAKE3-256 payload digest (multi-chunk port, was FNV-1a stand-in) | 2 gates; 3 sabotage twins; pinned frame KAT `54ee6f3c…` vs b3sum |
| `strata-ledger-pack` | S4 | — | Rust | Account conservation state machine; debit accumulation (duplicate-input defect fixed, 1d16f2472); receipt chaining via boundary-replay law; REUSE-ADAPTED from unibit-kernel | 3 gates (incl. OCEL conformance); 3 sabotage twins; witnessed-replay KAT; boundary-replay law in `verify.py` |
| `strata-chain-pack` | S5 | — | Rust | Block header, chain-validity law, deterministic fork choice; gate law REUSE-ADAPTED from unibit-kernel | 2 gates; 1 sabotage twin; shared-head KAT `05ea1aa0…` |
| `strata-store-pack` | S6 | — | Rust | `ContentStore` trait, inline SHA-256 keying, marker journal rollback, typed capacity/rollback refusals; greenfield | 2 gates; 4 sabotage twins; compile-fail court (unconstructible states) |
| `strata-net-pack` | S7/S9 | — | Rust | CLAP-PDU framing + BTreeSet mempool + capped peer table; hardening law (030); `MEMPOOL_LEDGER_ADMISSION` composition law (040, NECESSARY NOT SUFFICIENT for ledger admission, RDF-encoded with gate citations + Lean provenance) | 4 gates; 1 sabotage twin |
| `strata-consensus-pack` | S8 | — | Rust | Heaviest-chain fork choice as PN64-style lattice; `WORK_ACCUMULATOR = u128`; adversarial module (selfish-mining, eclipse, spam) | 2 gates; 3 sabotage twins |
| `strata-governance-pack` | X5/T11 | — | Rust | Constitutional-diff gate over sealed consensus constants (matching chain-pack `GENESIS_CONSTANTS`); out-of-constitution edits must fire the gate | 2 gates; 1 sabotage twin |
| `strata-audit-pack` | S10 | — | Rust | Fuzz/known-attack corpus manifest + self-contained audit runner over inline provenance COPIES of hash/merkle, tx decode, chain validation, tip selection, ledger conservation; 1000 LCG cases per target + 5 known-attack regressions; corpus 14 attacks (2 OPEN) | 2 gates; 0 twins (runner, not a twin-bearing engine) |

The signer S3 closure: the digest-domain tag binds tx payloads; the
cross-pack ML-DSA court refuses a flipped payload byte; the untagged twin is
caught in both directions (ledger #67). `strata-tx-pack` is honestly
UNSUPPORTED for compile-fail courts (no non-validating path exists to force,
ledger #66); `strata-store-pack` and the ledger gate state carry trybuild
compile-fail courts with exact E-codes.

## Ontology URNs and base IRIs

All sixteen packs use `ontology.ttl` at the pack root with base IRI
`https://strata.chatman.ai/ontology#`. Pack-specific prefixes:

| Pack | Prefixes |
|---|---|
| protocol | `pdu:`/`wire:` = `https://strata.chatman.ai/ontology/pdu#` / `.../wire#` |
| pn64 | (base `st:`) |
| signer | (base `st:`) |
| stratus | (base `st:`) |
| temprun | (base `st:`) |
| valve | `valve:` = `https://strata.chatman.ai/ontology/valve#`, plus `wire:` |
| tx | `tx:` = `https://strata.chatman.ai/ontology/tx#` |
| net | `net:` = `https://strata.chatman.ai/ontology/net#` |
| cas, hash, ledger, chain, store, consensus, governance, audit | (base `st:`) |

All packs carry empty `[capabilities].requires` by design: `qualify_packs.py`
qualifies every pack in isolation (single-pack `[packs]` capsule), so a
cross-pack require can never resolve there (FM-PACK-018/FM-PACK-014).
Cross-pack relationships are documentation-only via ontology comments — no
owl:imports, no code vendoring.

## CLAP/1.0 PDU header layout (big-endian, 64 bytes)

| Field | Offset | Length | Type | Notes |
|---|---|---|---|---|
| magic | 0 | 4 | u32 | `0x434C_4150` ("CLAP") |
| version | 4 | 1 | u8 | `0x01` |
| permutation | 5 | 1 | u8 | max 5; >5 fails closed at parse |
| reserved | 6 | 2 | — | must be zero |
| epoch nonce | 8 | 8 | u64 | |
| fuel lease | 16 | 8 | u64 | zero at the valve = `fuel_exhausted` |
| parent receipt digest | 24 | 32 | — | BLAKE3 digest, `wire:ReceiptDigest` |
| history quad count | 56 | 4 | u32 | N |
| candidate quad count | 60 | 4 | u32 | M |

Bytes 64 onward carry the N history quads then M candidate quads.

## Wire classes

| Class | Fixed length | Notes |
|---|---|---|
| `wire:ReceiptDigest` | 32 | BLAKE3 parent receipt digest |
| `wire:RefusalReceipt` | 32 | opaque, constant-time; no cause channel; strict parse fails closed otherwise |

## ML-DSA-65 attestation sizes (FIPS 204)

| Constant | Value |
|---|---|
| detached signature | 3309 bytes |
| encoded public key | 1952 bytes |
| seed | 32 bytes *(comment-level, not projected)* |
| attested payload | 72 bytes *(comment-level, not projected)* |

Default key: `st:DefaultKey`, key id `strata-default`, algorithm `ML-DSA-65`.

## PN64 Petri-net law

- One transition per u64 word; 16-bit place state word `m`.
- Enabled: `(m & pre) == pre`.
- Fire law: `m' = (m ^ pre) | post` (pre bits consumed, post bits set).
- Six canonical RONR transitions `t01`–`t06` (main motion through vote to
  adopt), with verb opcodes (e.g. `previous_question` = `0x05`).

## Temprun fuel admission

The temprun run/2 sieve charges 1 unit each for clock, coordinates, and
conformance — a run is admitted iff `fuel >= 3` (`st:admissionFuel`).

## Valve refusal atoms

Constant-time, fail-closed, Elixir module per atom
(`Strata.Valve.Refusals.*`). Internal atom taxonomy; the wire carries only the
opaque 32-byte receipt.

| Atom | Condition | Adversarial mirror |
|---|---|---|
| `malformed_frame` | strict 64-byte header match failed (bad magic/version, reserved, perm > 5, length) | `Eclipse` |
| `fuel_exhausted` | header fuel lease is zero, refused before arena handoff | `SpamFlood` |
| `parent_discontinuity` | parent receipt digest discontinuity | `SelfishMining` |
| `arena_failure` | arena-side failure during run | `InvalidBlockGossip` |

The additive `WindowCapacityRefusal` class (L86) mirrors knhk's exact
`guard_violation` atoms verbatim (read-only citation): run length
`Len =< 8` and epoch `Tau =< 8` — the Chatman constant k = 8, the
sliding-window capacity shared by both guards. The knhk-side parity KAT
fixture is `BLOCKED:merge-open` until that repo reopens (see Still-open).

## Shared constants and laws

- **32-byte receipts**: `wire:ReceiptDigest` and `wire:RefusalReceipt` are
  both fixed 32 bytes; the tx payload digest is BLAKE3-256 (32 bytes, pinned
  frame KAT `54ee6f3cee2f0d5fbdae268d411deb1ed6064bcfdf4163ebfa68e44615f9adf2`
  vs b3sum).
- **Shared-head KAT `05ea1aa0…`**: four PN64/OCEL64 dual-word entries
  (`sw:kat-entry-1`–`4`) folded by insa-proof's sync replay law and
  strata-protocol's logchain law into one shared head
  `05ea1aa096f45968aacb2c996d2b541e4b9fdef24f006e0204e1fa88d33f68a5`;
  `strata-chain-pack/witness.ttl` pins the head, `verify.py` recomputes it.
- **BLAKE3 logchain law** (`st:ChainRuleV2Fold`): base admission-frame chain
  hash, then the schema string and the full v2 epoch payload folded by BLAKE3
  over `base || schema || epoch_bytes`; strict no-op when v2 is None.
  Discriminator `CHAIN_RULE_V2_FOLD = "praxis-chain/v2-fold"`. Consumed by
  ggen-engine's receipt chain seam; KAT court in the hash template test
  module.
- **u128 work accumulator**: per-block work = `2^(PoW leading-zero bits)`,
  accumulated in u128. Per-block work saturates at 2^127; the u128 sum cannot
  saturate for any physically minable chain, so the heaviest-work order stays
  TOTAL — the retired u64 accumulator saturated both competing chains to
  `u64::MAX` and degenerated the fork-choice law (the `chain_work` saturation
  tie flagged in ledger #42 is fixed).
- **`MEMPOOL_LEDGER_ADMISSION`** (`st:CompositionLaw`, net-pack gate 040):
  mempool admission is NECESSARY NOT SUFFICIENT for ledger admission; encoded
  as RDF with gate citations + Lean provenance, fail-closed gate with
  mutation non-vacuity (ledger #69).
- **Chatman constant k = 8**: sliding-window capacity shared by the run
  length and epoch tau guards, admitted as `valve:WindowCapacityRefusal`
  semantics.

## Court surface

- **Sabotage twins**: twin-bearing `#[test]` modules live in the packs'
  `generated/*.rs`; 14 of 16 packs carry at least one `fn sabotage_*` twin on
  disk today (`strata-audit-pack` is the runner, not a twin-bearing engine;
  `strata-stratus-pack` carries none). The ledger records the twin program at
  13/16 with the remaining coverage holes documented with justification
  (#65, e1ee25fa2).
- **Compile-fail courts**: trybuild with exact E-codes — gate state and
  `recompute_root` are unconstructible; `strata-tx-pack` is honestly
  UNSUPPORTED (ledger #66).
- **Family determinism courts**: strengthened to 20/20 with +3
  `DRIFT_GUARDED` annotations alongside the BLAKE3 tx digest landing
  (ledger #70).
- **Boundary-replay law**: in the ledger pack's `verify.py`, mid-root pinned;
  a tamper below the boundary is caught ONLY by the boundary law
  (non-vacuity witnessed); length-mismatch input REFUSED (ledger #64).
- **Cross-pack ML-DSA court** (S3): byte-flip refuses; untagged twin caught
  in both directions (ledger #67).
- **Audit corpus**: 14 attacks, including `GgenUnionBindingLeak`
  OPEN-UPSTREAM and `WasmNonReproducibleBuild` OPEN (ledger #68).

## Witness surface

All sixteen packs ship a committed `witness.ttl` and `verify.py`:

- `witness.ttl` uses the `sw:` vocabulary (`sw:GateRun`); it records the
  `sw:syncedGraphHash` copied from the ggen v2 sync receipt at witness time
  (graph-level plus one per gate). These hashes are ggen BLAKE3-chain values,
  NOT plain sha256 of file bytes.
- `verify.py` re-runs every `gates/*.rq` SELECT against `ontology.ttl` via
  rdflib; exit 0 iff zero rows AND the on-disk gate set matches the witnessed
  set (else `REFUSED: gate-set mismatch`).
- Catalog tier flips to `verified` on these files' presence.
- The frozen-court qualification boundary (`BLOCKED:ggen-pin-26.8.11`) is
  documented in `docs/sjira/v26.10.8/SYNC-WAVE-RECEIPT.md`.

Lean witnesses live outside the packs and map onto pack laws:

| Lean theorem (mfact/castle) | Pack law | Standing |
|---|---|---|
| ledger conservation theorem (`aa3d793cf5`) | ledger-pack transition conservation | unconditional — the NoDupIds premise was dropped after the duplicate-input fix (#56/#58/#63); old counterexample theorem renamed with the fix citation |
| 5-theorem pipeline E2E (`cece0148fd` + castle `25ee42e`) | → `lean-witness/v1` JSONL → Replayed `EvidenceInput` | axiom footprints from `#print axioms`, never hardcoded (#74) |
| rank-1 Lean witness (L111) | Replayed EvidenceInput (#52) | landed |
| composition-law Lean provenance citations | net-pack `MEMPOOL_LEDGER_ADMISSION` | cited in the RDF law |

## Still-open laws

- **Ledger conservation is unconditional** (resolved, listed for contrast):
  duplicate-input value creation was proved in Lean (mfact `15fa5e91a7`),
  fixed by debit accumulation (1d16f2472), and the conservation theorem no
  longer needs NoDupIds (#56/#58/#63).
- **`chain_work` saturation is fixed** by the u128 accumulator (S8); the u64
  tie law is retired. The wire block ABI is unchanged.
- **Attack-case fuzzing of S9 valve paths** (X18, ledger #4) — mutate S10's
  known-attack seeds into corpus families against the S9 valve paths; the
  sabotage twin must discriminate. Closes S10's one open surface.
- **knhk-side window-capacity KAT fixture** — `BLOCKED:merge-open`; the RDF
  projection (`valve:WindowCapacityRefusal`) is the deliverable; parity
  fixture deferred until the knhk repo reopens.
- **Store `rollback_to` interleave hole** — flagged by the mfact Lean
  candidate scan (#42); fix lane L47; re-verify against the store engine
  before claiming closed.
- **Twin coverage holes** — 3 remaining holes documented with justification
  (#65); stratus (no twin) and audit (runner) are the on-disk holes today.

## Authority fence

All sixteen packs are observation/projection surface ONLY — they manufacture
constants, models, and self-contained Rust reference implementations from RDF;
none of them validates a live network, reaches consensus, or holds value.
Signing, key custody, and any actuation over a real chain remain out of scope
and with the consumer.

## Regeneration

Regenerate with `ggen sync run` from each pack directory; see
[../how-to/generate-from-strata-ontologies.md](../how-to/generate-from-strata-ontologies.md).
Never hand-edit `generated/`.
