# Challenger Value Framing Pack

This pack makes Challenger-style commercial framing an evidence-controlled projection rather than unconstrained marketing prose.

`claims + buyer context -> DfCM-preserved narrative frontier -> reversible brief -> receipt`

The six phases are **TEACH → REFRAME → RATIONAL_IMPACT → NEW_WAY → PROOF → TAKE_CONTROL**. `PROOF` accepts only `VERIFIED` claims with a source and exact 40-hex subject. Metrics require sources. Customer outcomes cannot be presented as facts unless verified. `ALIVE` cannot be used without standing evidence.

Buyer tailoring is a projection. It never changes canonical evidence. The pack's authority ceiling is SELECT/CONSTRUCT only: `actuation=false` and `irreversible_selections=0`.

## Court

```bash
python packs/challenger-value-framing-pack/reference/python/court.py
```

The conformance vectors cover valid replay plus unsupported claim kind, missing exact subject, metric-without-source, unsupported audience, unsupported ALIVE claim, outcome-as-fact, and missing-phase refusal.

The generated docs are projections from `ontology.ttl` via SPARQL and ggen. They are disposable; the ontology and conformance law are canonical.
