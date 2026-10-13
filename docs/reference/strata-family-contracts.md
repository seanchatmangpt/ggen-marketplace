# Reference: Strata family contracts

Exact contracts for the seven Strata packs. Two packs declare `status = "alpha"`
in `pack.toml` (`strata-protocol-pack`, `strata-valve-pack`); the other five
carry no status field (version 0.1.0). Values below are projected from the pack
ontologies except where noted as comment-level; the ontology is canonical. See
[../explanation/strata-family-design.md](../explanation/strata-family-design.md)
for rationale and
[../explanation/level5-diataxis.md](../explanation/level5-diataxis.md) for the
shared Diátaxis maturity doctrine this family's docs follow.

## Pack table

| Pack | Status | Output language | Projected artifacts |
|---|---|---|---|
| `strata-protocol-pack` | alpha | Rust | PDU frame constants (`pdu-constants` rule) and wire classes (`wire-constants` rule → `generated/wire_constants.rs`) |
| `strata-cas-pack` | — | Rust | Merkle commit / wormhole / snapshot frame types |
| `strata-pn64-pack` | — | Rust | PN64 mask tables (`pn64_masks`) |
| `strata-signer-pack` | — | Rust | ML-DSA-65 attestation constants |
| `strata-stratus-pack` | — | Rust | Witness valves + state registers |
| `strata-temprun-pack` | — | Rust | Fuel-lease arena table (`arena.rs`) |
| `strata-valve-pack` | alpha | Elixir | Refusal skeletons (`generated/refusals.ex`) |

## Ontology URNs and base IRIs

| Pack | Ontology source | Base IRI |
|---|---|---|
| protocol | `ontology.ttl` | `https://strata.chatman.ai/ontology#` (prefixes `pdu:`/`wire:` = `https://strata.chatman.ai/ontology/pdu#` / `.../wire#`) |
| cas | `ontology.ttl` | `https://strata.chatman.ai/ontology#` |
| pn64 | `ontology.ttl` | `https://strata.chatman.ai/ontology#` |
| signer | `ontology.ttl` | `https://strata.chatman.ai/ontology#` |
| stratus | `ontology.ttl` | `https://strata.chatman.ai/ontology#` |
| temprun | `ontology.ttl` | `https://strata.chatman.ai/ontology#` |
| valve | `ontology.ttl` | `https://strata.chatman.ai/ontology#` (prefix `valve: https://strata.chatman.ai/ontology/valve#`) |

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

| Atom | Condition |
|---|---|
| `malformed_frame` | strict 64-byte header match failed (bad magic/version, reserved, perm > 5, length) |
| `fuel_exhausted` | header fuel lease is zero, refused before arena handoff |
| `parent_discontinuity` | parent receipt digest discontinuity |
| `arena_failure` | arena-side failure during run |

## Readiness witnesses (2026-10-13)

Each of the 7 strata packs ships a committed `witness.ttl` and `verify.py`:

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

## Blockchain capability family (S1-S8)

Landed 2026-10-13, roadmap slices S1-S8 of
[../sjira/v26.10.8/STRATA-BLOCKCHAIN-ROADMAP.md](../sjira/v26.10.8/STRATA-BLOCKCHAIN-ROADMAP.md):

- `strata-hash-pack` (S1) — SHA-256 (FIPS 180-4, vector-verified) + Merkle
  tree (root + inclusion proofs) over 32-byte digests, property-tested;
  projects hash constants and a self-contained Rust implementation.
- `strata-tx-pack` (S2) — framed wire transaction model over CLAP-PDU
  conventions with replay guard; tx digest is an FNV-1a stand-in until the S3
  hash binding.
- `strata-chain-pack` (S5) — block header with parent-hash chaining over tx
  Merkle commits, chain-validity law (height continuity, parent-hash binding,
  tx cap, duplicate-tx refusal, monotonic timestamp slot, deterministic PoW),
  and deterministic fork choice; gate law REUSE-ADAPTED from unibit-kernel via
  ontology projection only.
- `strata-ledger-pack` (S4) — account-based conservation state machine
  (credit/debit conservation, double-spend refusal valve, overflow refusal,
  receipt chaining); REUSE-ADAPTED from unibit-kernel via ontology projection
  only; ships `witness.ttl` + `verify.py`.
- `strata-store-pack` (S6) — content-addressed storage (`ContentStore` trait)
  keyed by inline SHA-256 with marker journal rollback and typed
  capacity/rollback refusals; greenfield; ships `witness.ttl` + `verify.py`.
- `strata-net-pack` (S7) — CLAP-PDU message framing + mempool over the tx
  layer; mid-flight at wave close (gates/queries/templates landed, readiness
  witness pending).
- `strata-consensus-pack` (S8) — heaviest-chain fork choice over the chain
  layer's block shapes as the PN64-style transition lattice with consensus
  constants; mid-flight at wave close (only `pack.toml` landed).

Authority fence: all seven packs are observation/projection surface ONLY —
they manufacture constants, models, and self-contained Rust reference
implementations from RDF; none of them validates a live network, reaches
consensus, or holds value. Signing, key custody, and any actuation over a
real chain remain out of scope and with the consumer.

## Regeneration

Regenerate with `ggen sync run` from each pack directory; see
[../how-to/generate-from-strata-ontologies.md](../how-to/generate-from-strata-ontologies.md).
Never hand-edit `generated/`.
