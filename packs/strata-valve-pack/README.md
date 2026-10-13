# strata-valve-pack

Class: CapabilityPack. Profile: project. Authority: SELECT/CONSTRUCT only, no DO.

## Identity

Strata valve refusal taxonomy (constant-time, opaque, fail-closed) projected from RDF to Elixir refusal module skeletons. Requires no other pack.

## Capability surface

```bash
$ ggen pack capabilities strata-valve-pack
```

## Evidence boundary

Marketplace admission and ggen qualification of this bounded boundary only. Projected refusal modules are not a fail-closed enforcement boundary exercised on any runtime.

## S9 adversarial mirror (roadmap slice 9)

Comment-level citation only: each internal `valve:RefusalClass` carries a
`valve:adversarialMirror` IRI literal naming the consensus-pack
AdversarialCase it surfaces (MalformedFrame→Eclipse, FuelExhausted→SpamFlood,
ParentDiscontinuity→SelfishMining, ArenaFailure→InvalidBlockGossip).
`gates/030_adversarial_mirror.rq` fails closed unless all four consensus
IRIs are mirrored. No wire or behavior change: the wire still carries only
the opaque 32-byte RefusalReceipt.
