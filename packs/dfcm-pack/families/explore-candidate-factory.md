# Family: explore-candidate-factory

> Absorbed from `dfcm-explore-candidate-factory-pack` (v2.2.0 consolidation, 2026-10-01). Synthesized note —
> the satellite shipped no README; content recovered from its manifest, structure, and
> courts. Namespace moved verbatim to `ontology/explore-candidate-factory.ttl` (no IRI changed); gates live
> family-prefixed in `../../gates/`; algorithms preserved verbatim below this directory.
> Superseded with absorption: the satellite's `pack.toml` (this pack is the one admission
> unit) and its `ggen.toml` generation wiring (queries/templates preserved as modules,
> not re-wired — they predate strict-mode ORDER BY and stay verbatim).

Candidate-family seed corpus (23 family candidates + 105 selection queries; no gates, no
templates). Shares the `.../ggen-marketplace/dfcm/explore#` IRI space with
dfcm-explore-maximalist: pareto/mcts/psro/fixedpoint individuals and the property IRIs are
COMMON; the two models differ (factory: family/ctq* literals incl. ctqRollback;
maximalist: kind/rollbackCost, standing as IRI). The union is additive and SPARQL-safe
(no property IRI is used with incompatible value types in a way any gate observes); both
vocabularies stay disjoint at query level. Canonical family/technique corpus now lives in
`ontology/option-capital.ttl` (this factory was its source — dfcm:sourcePack
"dfcm-explore-candidate-factory-pack" individuals retain the provenance literal).
