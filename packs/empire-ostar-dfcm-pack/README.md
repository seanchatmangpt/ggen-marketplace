# EMPIRE OSTAR DfCM option-space pack

This pack is a separate, versionable DfCM extension to `empire-ostar-reconstitution-pack`. It does not mutate the original authority-vacuum observation graph and does not manufacture the missing OSTAR authority contract.

## Preserve

The observed case contains six labelled candidate capabilities. The already-admitted OSTAR closure contract permits five final dispositions and requires every disposition to occur at least once in a completed closure:

- `PRESERVED`
- `SUBSUMED`
- `REPLACED`
- `ARCHIVED`
- `REFUSED`

Before semantic evidence distinguishes candidates, the DfCM preservation surface therefore contains every surjective assignment from six capabilities to five dispositions:

```text
5! × S(6,5) = 120 × 15 = 1800
```

The number `1800` describes **syntactic closure candidates only**. It is not evidence that any candidate is semantically correct, authoritative, executable, or preferred.

## Fence

The option space is manufactured with:

```text
selection_state = UNSELECTED
claim_ceiling = SYNTACTIC_CLOSURE_ONLY
selection_authority = false
actuation_authority = false
constraint_authority = PRUNE_ONLY
```

Evidence may remove incompatible edges from the graph. A failed edge is topology, not graph failure; otherwise-lawful reversible alternatives remain represented.

No graph, template, SPARQL result, generated JSON, model output, or planner output may select a winning disposition vector. Selection requires a separately admitted authority contract. Consequential DO remains outside this pack and must cross the existing BRCE/receipt boundary.

## Generated consequence

The pack projects:

```text
empire/reconstitution/ostar/dfcm-config.json
```

That file supplies the deterministic structural contract consumed by the ggen-legacy DfCM option-graph constructor. The generated file is a consequence, not marketplace source authority.

## Falsifiers

The pack is invalid if the six-capability or five-disposition closure drifts, expected syntactic closure count differs from 1800, selection becomes pre-resolved, a pruning constraint acquires selection authority, direct actuation becomes possible, or an unselected option graph is represented as O* admission.
