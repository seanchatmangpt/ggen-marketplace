# Reference

`RebloomWave` defines `maxDepth`, `maxOrder`, `requiresReceipt`, and `grantsDoAuthority`. `CompositionCandidate` defines `uses`, `reversible`, `expectedReuse`, `capabilitySpaceDelta`, `qualification`, and `actuation`. Generation emits `rebloom.frontier.v1`, `rebloom.plan.v1`, and `rebloom.receipt.v1`. Admission refusals are `REFUSED[MISSING_FIELDS]`, `REFUSED[AMBIENT_DO_AUTHORITY]`, `REFUSED[UNRECEIPTED_REBLOOM]`, and `REFUSED[NON_EXPANDING_BOUND]`.
