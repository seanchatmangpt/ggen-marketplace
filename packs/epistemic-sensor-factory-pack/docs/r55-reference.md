# Reference: R55 independent consumer fanout

## Exact construction base

`b116088d8b6c6daf6595c3e9b30eb6bb58572f4b`

## Source surfaces

- grounded fixture: `fixtures/r55-independent-consumer-fanout.ttl`
- sensors: `queries/651_r55_*.rq` through `queries/700_r55_*.rq`
- execution court: `tests/run_r55_independent_consumer_fanout.py`
- receipt: `receipts/develop/2026-08-25-r55-independent-consumer-fanout.json`

## Admission dimensions

Identity, exact-head parity, bounded authority, reusable court, public ontology, replay, receipt return, ggen manufacture, dependency closure, deterministic projection, target-token linkage, qualification-path linkage and zero ambient consequential DO.

## Strict-generation correspondence

Broad exact-head qualification discovered an inherited deterministic-manufacture defect in `consumer-realization-frontier-pack`: its `frontier-cardinality` SELECT rule lacked `ORDER BY`, which real ggen rejects under strict mode. R55 repairs that query and adds `tests/test_generation_ordering.py`, so every SELECT query referenced by that pack's generation contract must carry deterministic ordering before the R55 court can pass.

## Crown

Target compatible-consumer factor: 10. Grounded independently-ready count at construction: 1. Shortfall: 9. `1000X=NOT_ADMITTED` until independent returned evidence and downstream causal yield support the multipliers.
