# Qualification — premature-actuation-survival-pack

The pack is declarative and grants no runtime authority. Its gates are
violation-row SELECT queries: zero rows is clean; one or more rows is a typed
refusal candidate for external admission machinery.

## Anti-vacuity fixtures

- `qualification/fixtures/pos_survival.ttl` must produce zero rows for every gate.
- `qualification/fixtures/neg_survival.ttl` contains one witness for every
  failure family:
  - wrong-subject DO,
  - unauthorized DO,
  - unadmitted DO,
  - unreceipted DO,
  - premature DO,
  - policy claiming ambient DO authority.

## Boundary

The pack does not compute Kaplan-Meier curves, RMST, hazard ratios, causal
effects, or production standing. `autofde-lab` owns survival analysis;
`gymact` owns scenario × policy experiment construction; BRCE remains the
only lawful DO path.

Runtime qualification evidence is intentionally not asserted in this document
until a consumer runs the pack through the marketplace qualification court.
