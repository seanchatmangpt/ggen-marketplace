# prior-art-admission-pack

A reusable machine contract for the Anti-Reinvention Law.

```text
UnknownToBuilder != Novel
UnknownToTeam != UnknownToField

retrieve -> reuse -> compose -> extend -> invent

NOVEL_GAP(C)
  only if
for every searched prior-art candidate E:
  E does not satisfy RequiredSemantics(C)
  under the same boundary and conditions
```

The pack distinguishes a candidate search from truth, authority, execution and standing. A search result never grants DO authority.

## Required novelty receipt

A `pa:Search` claiming `pa:NOVEL_GAP` must include:

- required semantics;
- searched references;
- one typed candidate failure for every searched reference;
- missing semantics for each failed candidate;
- a falsifier;
- no selected prior-art reference.

This makes research part of admission rather than an optional human habit.
