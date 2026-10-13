# strata-tx-pack

Class: CapabilityPack. Profile: project. Authority: SELECT/CONSTRUCT only, no DO.

## Identity

Strata transaction model (roadmap slice S2,
`docs/sjira/v26.10.8/STRATA-BLOCKCHAIN-ROADMAP.md`): Tx framing over the
CLAP-PDU conventions — inputs/outputs, full-canonical-serialization payload
digest, explicit
replay-guard nonce — projected as a self-contained serde-free Rust module.

## Capability surface

```bash
$ ggen pack capabilities strata-tx-pack
provides: urn:ggen:pack:strata-tx-pack, urn:strata:tx:model-v1
requires: (none — FM-PACK-018, see pack.toml)
```

## Wire format

Fixed-width, big-endian, varint-free (CLAP-PDU conventions; ground truth:
`packs/strata-protocol-pack/ontology.ttl`, cited by comment — no
`owl:imports`):

```text
header (TX_HEADER_LEN = 56):
  [0..4)   magic "STX1" (TX_MAGIC = 0x5354_5831)
  [4]      version TX_VERSION = 0x01
  [5..8)   reserved, must be zero
  [8..16)  u64 nonce (replay-guard field)
  [16..20) u32 input count
  [20..24) u32 output count
  [24..56) 32B payload digest (FNV-1a over the FULL canonical
           serialization — every wire field in fixed order; documented as
           NOT cryptographic; S3 upgrades to the real signer digest)
body: n * TxInput (36B = 32B prev TxId + u32 index)
      m * TxOutput (9B = u64 value + u8 value-unit tag)
```

## Gates

- `gates/010_tx_layout.rq` — offset abutment chain (offset+len = next offset,
  ends at TX_HEADER_LEN), offset-collision, constant-presence, and
  datatype/malformed-integer fail-closed arms (V7 pattern).
- `gates/020_tx_closure.rq` — the Tx field surface is EXACTLY
  {txNonce, inputCount, outputCount, valueUnit}: presence arms for the four
  model classes and four declared properties, plus an undeclared-property
  closure arm.

## Verification receipt (2026-10-13, L46 digest-coverage fix)

- `ggen sync run` x2 (+1 determinism re-check) → byte-identical
  `generated/` (sha256 `1bb139a2…` tx_consts.rs, `cf7bd6d0…` tx_model.rs).
- `rustc --test generated/tx_model.rs` → 13/13 pass: round-trip identity,
  1000-case byte-identical round-trip fuzz, truncated-decode fails, tampered
  digest detected, typed header errors, mutation courts over EVERY guarded
  field byte (header + NONCE + body elements), zero-unguarded-fields audit
  (every non-digest frame byte flips → typed refusal), digest-binding court
  (same tx → same digest; any single-byte change → different digest),
  replay-guard + sabotage-twin courts, projected-const abutment;
  `generated/tx_consts.rs` → 3/3 pass.
- Both gates 0 rows via rdflib (verify.py zero-rows).
- `scripts/qualify_packs.py --pack strata-tx-pack` → status ALIVE
  (consequence sha256 `85cddfeb…`).

## Evidence boundary

Marketplace admission and ggen qualification of this bounded boundary only.
The generated module is a wire-format model, not a verified ledger: the
payload digest is a deterministic (non-cryptographic) integrity digest, and
replay/ledger uniqueness enforcement is S4's valve, not this pack.
