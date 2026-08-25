# Reference: realization calibration hypergraph

The pack composes `Capability -> CompositionEdge -> Realization -> Calibration -> Frontier`. Public provenance uses PROV-O; descriptive typing uses DCTERMS/SKOS; authority is represented without granting execution authority.

Required edge facts: source capability, target capability, expected delta, successes, failures, reversibility. Optional but capital-bearing facts: expected reuse, marketplace support, missing primitive. Required current realization facts: exact subject, observed delta, standing, receipt digest, currentness.

Posterior variant: `(successes + 1) / (successes + failures + 2)`. Calibrated delta multiplies expected delta by that posterior. Reuse-adjusted yield multiplies calibrated delta by `1 + expectedReuse`. Conservative and optimistic queries remain separate alternatives. `80-calibrated-frontier.rq` excludes only strictly dominated reversible edges under posterior and reuse-adjusted yield.
