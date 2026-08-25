# How to add R27 portfolio observations

1. Resolve the repository/ref to an exact 40-hex SHA.
2. Add a `seed-observation` entity whose identifier ends in `@<sha>` and whose repository is explicit.
3. Link every discovered actionable opportunity with PROV `wasDerivedFrom`; never infer an unobserved counterfactual.
4. Mark novelty only when prior ledger evidence does not already contain the same opportunity signature.
5. Bind current observations to a measurement receipt carrying `OBSERVE|VERIFY` and zero DO.
6. Run the 30 R27 queries and preserve grounded misses, duplicate capital, stale evidence, split frontiers and zero-relief findings.
7. Append observation -> sensor -> opportunity -> subject -> standing -> provenance edges to the JSONL ledger.
8. Recompute E from admitted seed and actionable counts. Do not promote fixture or reference E to fleet truth.
9. Generate the R27 report/court through ggen; generated artifacts are consequences and must not be hand-edited.
10. Qualify the exact source head before using the result for downstream SELECT.
