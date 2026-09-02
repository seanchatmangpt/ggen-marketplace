# pragmatic-programmer-sparql-pack

Executable software-production standard work derived from a 100-practice, paraphrased Pragmatic Programmer surface.

## PragProg is the software TPS

This pack treats PragProg as the software-production analogue of the Toyota Production System:

- **Standard work** — the 100 tip courts define the current best-known production method.
- **Andon** — a non-zero SPARQL court result is a visible abnormality, not something to explain away.
- **Jidoka / built-in quality** — REFUSE, CARDINALITY, contract, provenance, and exact-execution courts stop defective state from acquiring standing.
- **Genchi genbutsu** — exact-subject execution, reproductions, diagnostics, benchmarks, and receipts outrank narrative claims.
- **Kaizen** — a finding drives observe → diagnose → repair → execute → permanent guard → standardize.
- **Poka-yoke** — contracts, ownership, cardinality, authority, and fail-closed rules prevent known error classes.
- **JIT / flow** — tracer paths, bounded transitions, small batches, low coupling, automation, and delivery-wait courts reduce queues and unfinished work.
- **Respect for people** — stakeholder provenance, user-context evidence, learning capitalization, communication intent, safety, and declared purpose keep optimization attached to human consequence.

The operational loop is:

`observe -> PragProg SPARQL court -> andon -> jidoka/refusal when required -> RCA -> ggen countermeasure -> exact execution -> receipt -> permanent guard -> revised standard work`

The metric is not used to blame the operator. Abnormal output is evidence about the production system and a demand for kaizen.

## Contract

Consumers opt a subject into a specific court with `pp:governedBy pp:tipNNN`. A gate returns zero rows when the governed observation satisfies the rule and one or more rows when it finds a violation/opportunity. Subjects not opted into a tip are ignored, so the pack composes safely with unrelated ontologies.

`./tps/profile.ttl` declares `pp:PragProgTPS`, includes all 100 tips, and maps each tip to one or more TPS mechanisms. `./tps/coverage.rq` must return zero rows. `./tps/control-surface.rq` exposes the complete standard-work/control mapping for analysis.

The queries are source policy, not generated output. The ontology declares the tip identities and observation vocabulary.

## Validation

The original 100 courts were validated by parsing every SPARQL 1.1 query with RDFLib, executing every court against an empty baseline (0 findings), and executing every court against a synthetic violating observation (>=1 finding).

The TPS profile is separately RDF-parsed and the completeness query proves 100/100 tip coverage with zero unmapped tips.
