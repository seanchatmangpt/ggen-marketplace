# strata-signer-pack

Class: CapabilityPack. Profile: project. Authority: SELECT/CONSTRUCT only, no DO.

## Identity

Detached-signature attestation for Strata: attestation keys and detached signatures (ML-DSA-65, 1952-byte public key / 3309-byte signature) over receipts and frames carried by the CLAP-PDU protocol types from strata-protocol-pack; S3 adds a signing trait + tx-digest binding layer.

## Capability surface

```bash
$ ggen pack capabilities strata-signer-pack
```

## Signing layer (S3)

`generated/signing.rs` (rule `digest-binding`) projects a `PayloadSigner` trait
(sign/verify, 3309-byte detached signatures) plus a `TxSigner` adapter whose
`bind_tx_digest` maps raw tx bytes to a 32-byte SHA-256 digest
(`st:TxDigestBinding`; gated by `gates/020_digest_binding.rq`). The real
ML-DSA-65 backend is the ml-dsa crate behind `~/strata/strata_protocol/src/signer.rs`;
consumers inject it through the trait. The in-template `TestSigner` used by the
generated tests is a documented test double, not a crypto implementation. The
SHA-256 in `signing.rs` is an inline provenance copy of
strata-hash-pack's generated primitive (cross-pack consumption of a
per-pack-generated module would couple two generated artifacts; self-contained
wins).

## Evidence boundary

Marketplace admission and ggen qualification of this bounded boundary only. Projected signer skeletons are not a qualified cryptographic signing implementation on any runtime.
