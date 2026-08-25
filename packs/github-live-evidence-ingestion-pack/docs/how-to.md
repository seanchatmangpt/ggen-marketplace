# How to qualify ingestion replay

1. Save captured GitHub response envelopes as immutable inputs.
2. Run each envelope through `runtime/normalize.py` twice and compare bytes.
3. Run `gates/exact_subject.py`, `gates/authority_fence.py`, and `gates/receipt_fence.py`.
4. Combine normalized JSONL with `runtime/lineage.py`; retain every emitted lineage edge.
5. Partition the observations with `runtime/bundle.py` and verify no observation crosses an exact-subject boundary.
6. Run the pack test suite and the repository marketplace qualification court.
7. Treat resulting observations as evidence only; they carry no deploy, release, merge, or external-system authority.
