# Qualification

The marketplace validator may establish only pack-structure standing. Full qualification additionally requires a real `ggen` consumer run that:

1. binds one admitted `frf:Opportunity` and `frf:Benchmark`;
2. renders the working-backwards release and acceptance contract;
3. refuses an incomplete opportunity through `010_required_opportunity_fields.rq`;
4. refuses an earned release without an ALIVE evidence receipt through `020_earned_release_evidence.rq`;
5. demonstrates deterministic replay of the same source graph and template set;
6. renders an earned release only after exact-subject execution evidence exists.

Until that consumer execution is observed, this pack is `PARTIAL_ALIVE` at most; template presence is not execution.
