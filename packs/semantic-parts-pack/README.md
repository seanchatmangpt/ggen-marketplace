# semantic-parts-pack

Ontology and fail-closed admission law for software-part discovery inspired by
CodeGraph (arXiv:2609.29474) without copying its file-level taxonomy into an
execution model.

The pack keeps four observations distinct: algorithm, domain, programming
paradigm, and design pattern. Public grounding such as Wikidata is evidence for
semantic identity. A matching part is still only a `CANDIDATE` with
`authorityBoundary "NONE"`.

The key boundary is:

```text
observe taxonomy -> ground -> discover candidate -> independent behavioral verifier
                 -> admitted replacement -> authorized DO elsewhere
```

The SPARQL gate returns violations. A clean result has zero rows. In particular,
CodeGraph evidence alone can never promote a substitution to `sp:Verified`.
