# pragmatic-programmer-sparql-pack

Reusable SPARQL courts for a 100-practice, paraphrased Pragmatic Programmer policy surface.

## Contract

Consumers opt a subject into a specific court with `pp:governedBy pp:tipNNN`. A gate returns zero rows when the governed observation satisfies the rule and one or more rows when it finds a violation/opportunity. Subjects not opted into a tip are ignored, so the pack composes safely with unrelated ontologies.

The queries are source policy, not generated output. The ontology declares the tip identities and observation vocabulary.

## Validation

The pack was validated by parsing all 100 SPARQL 1.1 queries with RDFLib, executing every court against an empty baseline (0 findings), and executing every court against a synthetic violating observation (>=1 finding).
