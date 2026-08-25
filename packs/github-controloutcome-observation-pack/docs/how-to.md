# How to qualify exact-head observations

1. Capture run/job/PR facts without mutating GitHub state.
2. Bind every observation to repository, exact head SHA, run attempt, and receipt digest.
3. Execute `gates/exact_subject.py`, `gates/authority_fence.py`, and `gates/receipt_fence.py`.
4. Evaluate all query variants; do not discard failed edges.
5. Generate ledger/court outputs with the matching ggen runtime.
6. Re-run and compare outputs byte-for-byte before treating the projection as replayable evidence.
