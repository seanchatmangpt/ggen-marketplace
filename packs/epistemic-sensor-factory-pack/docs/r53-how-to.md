# How-to — qualify a causal propagation edge

For each candidate edge, require an exact source consumer, a returned/replayable receipt, a downstream opportunity, temporal ordering, and an independent target evidence root. Record confidence explicitly and keep standing/authority transfer false.

Run the same dependency-free courts used by the exact-head qualification rail:

```bash
python3 packs/epistemic-sensor-factory-pack/tests/test_r53_static_contract.py
python3 packs/epistemic-sensor-factory-pack/tests/test_r53_causal_propagation.py
```

The RDF court requires `rdflib==7.1.4`; it intentionally does not require pytest. A missing causal or counterfactual witness is an observation gap, not permission to infer causality. Generated plans are SELECT/CONSTRUCT consequences and carry no DO authority.
