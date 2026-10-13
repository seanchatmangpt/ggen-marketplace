# strata-signer-pack

Class: CapabilityPack. Profile: projection. Authority: SELECT/CONSTRUCT only, no DO.

## Identity

Detached-signature attestation for Strata: attestation keys and detached signatures (ML-DSA-65, 3309-byte public key / 1952-byte signature) over receipts and frames carried by the CLAP-PDU protocol types from strata-protocol-pack.

## Capability surface

```bash
$ ggen pack capabilities strata-signer-pack
```

## Evidence boundary

Marketplace admission and ggen qualification of this bounded boundary only. Projected signer skeletons are not a qualified cryptographic signing implementation on any runtime.
