# strata-tx-pack

Class: CapabilityPack. Profile: project. Authority: SELECT/CONSTRUCT only, no DO.

## Identity

Strata transaction model (roadmap slice S2,
`docs/sjira/v26.10.8/STRATA-BLOCKCHAIN-ROADMAP.md`): Tx framing over the
CLAP-PDU conventions — inputs/outputs, payload-digest placeholder, explicit
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
  [24..56) 32B payload digest (PLACEHOLDER — FNV-1a stand-in over (n, m);
           S3 binds the real signer digest)
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

## Verification receipt (2026-10-13, this working tree)

- `ggen sync run` x2 → byte-identical `generated/` (sha256
  `1bb139a2…` tx_consts.rs, `3b5ffd0e…` tx_model.rs).
- `rustc --test generated/tx_model.rs` → 6/6 pass (round-trip identity over
  sampled (seed, n, m), truncated-decode fails, tampered digest detected,
  typed header errors, replay-guard court, projected-const abutment);
  `generated/tx_consts.rs` → 3/3 pass.
- Both gates 0 rows via rdflib 7.6.0.
- `scripts/qualify_packs.py --pack strata-tx-pack` → status ALIVE
  (consequence sha256 `bc302903…`).

## Evidence boundary

Marketplace admission and ggen qualification of this bounded boundary only.
The generated module is a wire-format model, not a verified ledger: the
payload digest is a documented placeholder, and replay/ledger uniqueness
enforcement is S4's valve, not this pack.
