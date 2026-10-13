# strata-cas-pack

Class: CapabilityPack. Profile: project. Authority: SELECT/CONSTRUCT only, no DO.

## Identity

Content-addressed storage for Strata: Merkle commits, knowledge wormholes (addressable cross-graph links), and snapshots. Frames commits over the CLAP-PDU protocol types from strata-protocol-pack. Witnessed sample individuals (3 commits, 1 wormhole, 1 snapshot) ground the canonicalization law (digest = lowercase-hex SHA-256 of the declared canonical payload); gates live under `gates/` wired in `ggen.toml`, runtime courts in `generated/cas.rs` `mod tests`.

## Capability surface

```bash
$ ggen pack capabilities strata-cas-pack
```

## Evidence boundary

Marketplace admission and ggen qualification of this bounded boundary only. Projected storage skeletons are not a running, qualified content-addressed store on any consumer runtime.
