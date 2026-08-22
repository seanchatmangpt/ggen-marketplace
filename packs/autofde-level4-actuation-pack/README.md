# autofde-level4-actuation-pack

Admits OCEL-projected actuation logs against the real Level-4 causal-chain SHACL shapes.
It does not itself produce actuation logs; it validates that a data graph already
projected from an OCEL 2.0 log (see `autofde_lab.ocel.rdf_projection.project_log_to_graph`
in the source repository this ontology comes from) obeys the causal chain:

```
Actuation -> PostconditionObservation -> Receipt -> Replay
ProbeExecuted (>=1, strictly before) -> ModelInferred
```

## Source of truth

`ontology/level4-chain.shacl.ttl` is copied verbatim from
`ontologies/autofde/level4-chain.shacl.ttl`. Its own header states, and this pack
respects, that these shapes are **the only expression of these constraints** — nothing
here re-states the causal-chain logic in Python. The header also documents exactly which
parts are SHACL Core (cardinality/class checks, qualified value shapes over an inverse
path) and which parts require `sh:sparql` (cross-node timestamp and digest comparisons
that SHACL Core's `sh:lessThan` cannot express, since the compared values live on
different event nodes, not on the same focus node).

## Gate

`gates/010_level4_conformance.py` loads a data graph (default:
`qualification/consumer.ttl`) and the shapes graph, then calls `pyshacl.validate()` for
real. It prints `{"conforms": bool, "violation_count": int, "violations": [...]}` to
stdout and exits nonzero when the data graph does not conform.

```bash
python3 packs/autofde-level4-actuation-pack/gates/010_level4_conformance.py \
    --data packs/autofde-level4-actuation-pack/qualification/consumer.ttl
```

## Fixtures

- `qualification/consumer.ttl` — minimal fixture that conforms to every shape (verified:
  `conforms: true`, `violation_count: 0`).
- `qualification/broken-example.ttl` — identical except the `Replay`'s `head_digest` does
  not match its `Receipt`'s `receipt_digest`, which the `sh:sparql` half of
  `Level4ReplayShape` refuses (verified: `conforms: false`, one violation naming
  `Level4ReplayShape` / `SPARQLConstraintComponent`).
