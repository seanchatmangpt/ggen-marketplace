# Reference — R77 exact repository universe

Canonical collector: `scripts/r77_repository_universe.py`.

Inputs: GitHub owner, UTC observation timestamp, optional `GITHUB_TOKEN`. Authenticated mode reads `/user/repos` and filters exact owner identity; public mode reads `/users/{owner}/repos` and is `PARTIAL_ALIVE` for reachability completeness.

Outputs: deterministic Turtle `RepositoryUniverse` + `RepositorySnapshot` entities. R77 supplies 50 SPARQL sensors. Exact standing uses `UNKNOWN | PARTIAL_ALIVE | ALIVE | BUILD_BROKEN | UNSUPPORTED | REFUSED[...]` and never promotes workflow existence to execution evidence.

RevenueFROMCustomer and RevenueFORCustomer are separate evidence classes. Consequential DO is prohibited by the pack authority policy.
