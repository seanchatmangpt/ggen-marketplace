# Reference: Strata family contracts

Exact contracts for the seven Strata packs (all status **alpha**). Every value
below is projected from the pack ontology; the ontology is canonical. See
[../explanation/strata-family-design.md](../explanation/strata-family-design.md)
for rationale and
[../explanation/level5-diataxis.md](../explanation/level5-diataxis.md) for the
shared Diátaxis maturity doctrine this family's docs follow.

## Pack table

| Pack | Status | Output language | Projected artifacts |
|---|---|---|---|
| `strata-protocol-pack` | alpha | Rust | PDU frame constants (`pdu-constants` rule) |
| `strata-cas-pack` | alpha | Rust | Merkle commit / wormhole / snapshot frame types |
| `strata-pn64-pack` | alpha | Rust | PN64 mask tables (`pn64_masks`) |
| `strata-signer-pack` | alpha | Rust | ML-DSA-65 attestation constants |
| `strata-stratus-pack` | alpha | Rust | Witness valves + state registers |
| `strata-temprun-pack` | alpha | Rust | Fuel-lease arena table (`arena.rs`) |
| `strata-valve-pack` | alpha | Elixir | Refusal skeletons (`generated/refusals.ex`) |

## Ontology URNs and base IRIs

| Pack | Ontology source | Base IRI |
|---|---|---|
| protocol | `ontology.ttl` | `urn:strata:protocol:` (prefixes `pdu:`/`wire:` = `urn:strata:protocol:pdu#` / `...:wire#`) |
| cas | `ontology.ttl` | `https://strata.chatman.ai/ontology#` |
| pn64 | `ontology.ttl` | `https://strata.chatman.ai/ontology#` |
| signer | `ontology.ttl` | `https://strata.chatman.ai/ontology#` |
| stratus | `ontology.ttl` | `https://strata.chatman.ai/ontology#` |
| temprun | `ontology.ttl` | `https://strata.chatman.ai/ontology#` |
| valve | `ontology.ttl` | `urn:strata:valve:` (prefix `valve: urn:strata:valve#`) |

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
| seed | 32 bytes |
| attested payload | 72 bytes |

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

## Regeneration

Regenerate with `ggen sync run` from each pack directory; see
[../how-to/generate-from-strata-ontologies.md](../how-to/generate-from-strata-ontologies.md).
Never hand-edit `generated/`.
