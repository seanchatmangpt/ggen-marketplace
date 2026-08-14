# Fortune 5 Enterprise Architecture Pack

Semantic supply for the AutoFDE role-conditioned planner league and Fortune-5 enterprise architecture crown.

## Separation of responsibilities

```text
Marketplace ontology / public semantics
        ↓
      ggen
 deterministic projection
        ↓
   AutoFDE-Lab
 planner population / meta-planning
        ↓
 typed next-edge candidate
        ↓
      BRCE
        ↓
 GymAct/runtime consequence
        ↓
 observation / receipt / replay
```

This pack grants **no DO authority**. Planner, policy, role, agent and authority are distinct objects.

## Composition law

The admission query deliberately does not validate every public-vocabulary subject in a composed graph. Fortune-5-specific obligations apply only to pack-owned typed individuals and/or resources that explicitly opt into `ea:Fortune5EnterpriseProfile`.

Required invariant:

`Court_F5(G) = Court_F5(G restricted to Fortune5 profile members)`

This prevents the pack from seizing semantic jurisdiction over foreign `prov:Agent`, `prov:Entity`, SKOS concepts, DQV measurements, or future Marketplace vocabularies.

## Core semantic surface

- 12 architecture principles
- 12 architecture viewpoints
- 9 governance gates
- planner roles: accomplish, falsify, diagnose, recover, architect, world generator, reward falsifier, assumption falsifier, meta-selector
- decision/evidence concepts
- enterprise architecture crown

## Cross-repo consumers

- `autofde-lab`: role-conditioned planner league, enterprise planning PDDL and meta-selection
- `gymact`: bounded shared-world execution and WorldCyber runtime
- `ggen`: deterministic semantic projection
- `wasm4pm`/process intelligence: observed process/conformance evidence

Claim ceiling: `CANDIDATE_SEMANTIC_SUPPLY_NO_RUNTIME_AUTHORITY`.
