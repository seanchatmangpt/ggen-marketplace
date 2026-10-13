# strata-cas-pack

Class: CapabilityPack. Profile: project. Authority: SELECT/CONSTRUCT only, no DO.

## Identity

Content-addressed storage for Strata: Merkle commits, knowledge wormholes (addressable cross-graph links), and snapshots. Frames commits over the CLAP-PDU protocol types from strata-protocol-pack. Empty projections are REFUSED by design; gates live under `gates/` wired in `ggen.toml`.

## Capability surface

```bash
$ sed -n '/[capabilities]/,/\[/p' packs/strata-cas-pack/pack.toml
```

## Evidence boundary

Marketplace admission and ggen qualification of this bounded boundary only. Projected storage skeletons are not a running, qualified content-addressed store on any consumer runtime.
