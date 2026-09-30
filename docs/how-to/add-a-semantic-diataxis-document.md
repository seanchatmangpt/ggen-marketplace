# How to add a document to the semantic Diátaxis pack

1. Add an `sd:Document` to `packs/sa2a-semantic-diataxis-pack/ontology.ttl` with `sd:title`, exactly one `sd:quadrant`, `sd:capability`, a unique `sd:outputId`, a 40-hex `sd:subjectRevision`, `sd:authority "NONE"` and an `sd:standing`.
2. For a `tutorial` or `how-to`, add `sd:hasStep` steps with unique integer `sd:order` and an `sd:action`.
3. Mark a step `sd:consequential true` only with an `sd:externalAuthority` the document does not grant itself.
4. Claim `ALIVE` only with `sd:evidence`.
5. Run `python3 -m pytest tests/test_sa2a_semantic_diataxis_pack.py -q` and `python3 scripts/marketplace.py validate`.
