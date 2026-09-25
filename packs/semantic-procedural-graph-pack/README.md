# Semantic Procedural Graph Pack

SPG is an interchange boundary, not another planner or workflow engine.

The pack reuses public semantics where they already exist:

- P-Plan for plan/step identity,
- PROV-O for provenance-bearing entities,
- DCTERMS for source metadata,
- SKOS for controlled concepts,
- SHACL for graph admission.

It mints only the remainder needed to reify procedural transitions with guards, evidence, authority, consequence, receipt and falsifier semantics, plus projection bindings and prior-art novelty claims.

## Anti-Reinvention Law

A `spg:NovelGap` is not "the team has not seen this before." It is the residual after prior-art candidates have been searched and each candidate's missing semantics have been typed.

```text
UnknownToBuilder != Novel
retrieve -> reuse -> compose -> extend -> invent
```

## Authority ceiling

This pack performs no consequential actuation. An SPG may describe a consequential transition, but its shape requires explicit authority, a consequence receipt, and a falsifier. Runtime DO remains outside this pack and behind BRCE.

## First consumer

The first court binds one SA2A -> BRCE procedure to stable semantic identities and projects those identities into HDDL, TLA+, OCEL 2.0, SA2A, and BRCE surfaces.
