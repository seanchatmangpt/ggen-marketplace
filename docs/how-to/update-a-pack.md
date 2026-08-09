# How to update a pack

1. Read the pack's current manifest, ontology, templates, gates, and README.
2. Identify whether the change is semantic (RDF), projection (template), admission control (gate), or metadata.
3. Make the smallest coherent source change. Do not patch a consumer-generated output instead.
4. Bump `[pack].version` when the pack's published behavior or contract changes.
5. Run marketplace validation and deterministic catalog projection.
6. For behavioral changes, run the pack through ggen against representative consumer RDF and prove replay/idempotency.
7. Publish through a purpose branch and PR with the exact verification subject.
