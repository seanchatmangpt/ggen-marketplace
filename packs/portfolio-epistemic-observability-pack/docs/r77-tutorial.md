# Tutorial — materialize the exact reachable repository universe

1. Resolve an observation timestamp in UTC.
2. Run `python packs/portfolio-epistemic-observability-pack/scripts/r77_repository_universe.py --owner seanchatmangpt --observed-at <UTC> --output /tmp/repos.ttl`.
3. Parse `/tmp/repos.ttl` with the R76 + R77 ontologies.
4. Execute `queries/r77/*.rq` to expose missing heads, structural projections, GGEN paths, qualification, throughput, OCEL, and revenue-evidence gaps.
5. Treat unauthenticated census output as `PARTIAL_ALIVE`; authenticated owner census may be admitted only with its exact receipt and timestamp.

The collector is read-only. Generated frontiers are consequences, not editing surfaces.
