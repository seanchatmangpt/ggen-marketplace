# Qualification — premature-actuation-survival-pack

The pack is declarative and grants no runtime authority. Its gates are
violation-row SELECT queries: zero rows is clean; one or more rows is a typed
refusal candidate for external admission machinery.

## Executable witness court

`gate-court.toml` binds every gate by exact stem to one clean witness and one
single-fault falsifier. `runners/semantic_runner.py` executes all survival
SPARQL gates with RDFLib and enforces:

- every pass witness produces zero rows across the entire gate set,
- every fail witness fires its named gate,
- no fail witness accidentally fires a second gate.

The exact-head workflow runs 6 gates x 2 expectations = 12 executable cases.

## Failure families

The court covers:

- wrong-subject DO,
- unauthorized or unadmitted DO,
- unreceipted DO,
- premature DO before the terminal predicate,
- policy claims of ambient DO authority,
- guard candidates that carry authority or claim installation before a
  separate admission/authority path.

## Recurrence projection

`queries/10_failure_guard_frontier.rq` maps observed invalid DO facts onto the
same guard ids manufactured by autofde-lab recurrence analysis. The result is a
candidate frontier only. `queries/20_policy_matrix.rq` exposes policy factors
whose `grantsDoAuthority` value is false.

## Boundary

The pack does not compute Kaplan-Meier curves, RMST, causal effects, or
production standing. `autofde-lab` owns survival analysis and replay receipts;
`gymact` owns scenario/policy/factorial experiment construction and manifest
closure; BRCE remains the only lawful DO path.

A green witness court proves the declared gates distinguish their supplied
positive and negative witnesses at the exact tested head. It does not imply
production standing for a consumer.
