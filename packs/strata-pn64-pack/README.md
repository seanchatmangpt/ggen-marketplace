# strata-pn64-pack

Class: CapabilityPack. Profile: project. Authority: SELECT/CONSTRUCT only, no DO.

## Identity

PN64/OCEL64 dual-word ABI for Strata: one Petri-net transition per 64-bit word (marking/W-/W+/tid/flags fields) plus the six canonical RONR procedural transitions as pre/post place masks, projected as a Rust module of `pub const` values.

## Capability surface

```bash
$ ggen pack capabilities strata-pn64-pack
```

## Evidence boundary

Marketplace admission and ggen qualification of this bounded boundary only. Projected ABI constants are not a verified Petri-net execution engine on any runtime.
