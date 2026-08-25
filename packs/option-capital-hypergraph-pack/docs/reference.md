# Reference

## Core entities

`oc:Capability` is an observed reusable capability. `oc:Composition` is a reversible set of two or three capability members. `oc:Candidate` is an executable alternative attached to one composition. `oc:OpportunityEdge` is the canonical ledger edge.

## Required opportunity-edge predicates

`oc:capability`, `oc:composition`, `oc:candidate`, `oc:repository`, `oc:marketplaceSupport`, `oc:missingPrimitive`, `oc:qualification`, `oc:reversibility`, `oc:expectedReuse`, and `oc:expectedCapabilitySpaceDelta`.

## Authority

The explorer has `SELECT|CONSTRUCT|VERIFY`. Generated ledger/frontier artifacts are projections and carry no DO authority. Any source fact with `oc:actuationPerformed true` is refused by the pack gate.

## Bounds

Composition order is 2–3. Executable candidates must declare `missingPrimitive "NONE"`. Reversibility and non-domination are explicit source facts rather than inferred ambient permissions.
