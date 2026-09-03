# pragmatic-programmer-sparql-pack

Reusable SPARQL courts for a 100-practice, paraphrased Pragmatic Programmer policy surface, promoted to the software-production TPS profile.

## TPS contract

The 100 courts are standard work. Non-zero findings are andon observations; hard refusal/cardinality/contract courts provide jidoka and built-in quality; exact execution supplies genchi genbutsu; repeated findings become kaizen demand and should be capitalized as ggen countermeasures and permanent guards.

`tps/profile.ttl` maps all 100 practices to TPS mechanisms. `tps/coverage.rq` refuses an unmapped practice and `tps/control-surface.rq` exposes the resulting standard-work surface.

Consumers opt a subject into a specific court with `pp:governedBy pp:tipNNN`. A gate returns zero rows when the governed observation satisfies the rule and one or more rows when it finds a violation/opportunity. Subjects not opted into a tip are ignored, so the pack composes safely with unrelated ontologies.

`templates/runtime-witness.txt.tmpl` is an intentionally non-authoritative deterministic consequence required by the real ggen pack-consumer contract. It proves the pack can be loaded through `ggen sync`; it is not compliance evidence and does not satisfy any PragProg court.

The queries are source policy, not generated output. The ontology declares the tip identities and observation vocabulary.

## Validation

The 100 courts were validated by parsing all SPARQL 1.1 queries with RDFLib, executing every court against an empty baseline (0 findings), and executing every court against a synthetic violating observation (>=1 finding). Marketplace and consumer qualification must additionally prove the pack loads through the real ggen runtime.
