# How to qualify R56

1. Materialize the exact R56 PR head; never substitute a later branch head.
2. Run marketplace validation before the R56 court.
3. Install RDFLib 7.x in the validation capsule.
4. Execute `python3 packs/epistemic-sensor-factory-pack/tests/run_r56_combinatorial_consumer_portfolio.py`.
5. Require `R56_QUERY_COUNT=50`, `R56_PAIR_COUNT=6`, `R56_TRIPLE_COUNT=4`, `R56_CLEAN_COMBINATORIAL_FRONTIER=1`, and `R56_COMBINATORIAL_CONSUMER_PORTFOLIO=ALIVE` for the grounded four-consumer specimen.
6. Run the repository-wide real-ggen qualification shards. R56 ALIVE does not waive failures elsewhere in the pack corpus.
7. If the base or head moves, invalidate integration standing and repeat exact-head qualification.

A failed scalar/cardinality assertion is a falsifier for the fixture/query correspondence. A failed real-ggen shard is a canonical pack repair edge, not permission to edit generated output or weaken the court.
