# Tutorial: observe an autonomic run through closure

1. Materialize an exact run subject with `runId`, `subjectSha`, cell, authority, start time, and RUNNING standing.
2. Append ordered checkpoints for PRE_ACTUATION, FIRST_COMMIT, PR_OPEN, QUALIFIED, MERGED, and MEMORY_COMPLETE as they are actually observed.
3. Record counts for meaningful commits, opportunities, merges, receipts, polls, head moves, API failures, and queue time.
4. Execute queries `2001`–`2050` over the admitted graph.
5. Promote ALIVE only when terminal time, receipt, exact subject, and closure evidence agree. A missing edge remains observable rather than being inferred away.
