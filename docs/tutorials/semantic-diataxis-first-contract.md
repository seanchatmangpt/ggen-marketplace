# Tutorial: admit your first semantic Diátaxis contract

This walkthrough admits the `sa2a-semantic-diataxis-pack` source and shows one refusal.

1. Run `python3 -m pytest tests/test_sa2a_semantic_diataxis_pack.py -q`. Nine gates admit `ontology.ttl` with zero violation rows.
2. In a scratch copy, change a document's `sd:subjectRevision` to `"main"`.
3. Re-run the test's gate query for `050_exact_identity`. It now returns a row: mutable refs are refused.

You have seen the pack accept a lawful source and refuse an unlawful one. Nothing was manufactured or executed.
