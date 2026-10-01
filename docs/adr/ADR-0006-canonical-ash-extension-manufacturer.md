# ADR-0006: Canonical Ash Extension Manufacturer

## Status
Accepted

## Context
`packs/ash-extension-pack/pack.toml` already states that
`ash-extension-core-pack` and `ash-extension-starter-pack` were consolidated and
superseded, but both legacy generic pack trees were still present in the repository.
That physical state contradicted the declared architecture and made it possible for future
work to extend or copy the obsolete manufacturers.

The broader Ash ecosystem also exposes a recurring pattern: reusable extension behavior is
best represented as declarative Spark semantics plus transformers, verifiers, Info
introspection, installers, execution realizations, and evidence. Creating a new marketplace
pack for each newly discovered Ash pattern fragments that semantic surface.

## Decision
1. **One canonical generic Ash-extension manufacturer**:
   `packs/ash-extension-pack` owns reusable Ash/Spark extension manufacturing semantics.

2. **Remove superseded generic manufacturers**:
   `ash-extension-core-pack` and `ash-extension-starter-pack` are deleted. Their
   generalized behavior already lives in the canonical pack.

3. **Mandatory search order**:
   `REUSE -> COMPOSE -> EXTEND -> INVENT`. Reusable gaps extend the canonical pack.
   Creating a sibling generic Ash-extension pack is not a valid resolution path.

4. **Spark is the semantic waist**:
   qualification targets both
   `implementation_semantics - spark_semantics = {}` and
   `spark_semantics - consumed_semantics = {}`, modulo explicitly classified
   non-semantic implementation mechanics.

5. **Framework names are realizations, not semantic authorities**:
   Reactor, AshOban, AshStateMachine, Splode, Igniter, and similar libraries may realize
   canonical capability families. Their implementation identity does not define the
   capability semantics.

6. **Domain authority remains separate**:
   packs that carry independent GraphLaw, R2RML, P-PLAN, PROV-O, OCEL, SA2A, or other
   domain meaning remain separate. Reusable Ash projection patterns discovered there are
   generalized back into `ash-extension-pack`.

7. **HDDL governs the manufacturing lifecycle**:
   `packs/ash-extension-pack/planning/vision2040.hddl` encodes the canonical
   OBSERVE -> ADMIT -> PLAN -> CONSTRUCT -> PROJECT -> COMPOSE -> QUALIFY -> STAND -> LEARN
   lifecycle. Burn-in is a qualification method, not a separate pack.

## Consequences
- Future generic Ash-extension work has one obvious home.
- Existing domain-specific packs become consumers/profiles of the canonical manufacturer
  instead of competing sources of Ash-extension mechanics.
- Surviving mutation/burn-in gaps recursively enlarge the canonical capability vocabulary.
- Marketplace structure now matches the consolidation claim in the canonical manifest.
