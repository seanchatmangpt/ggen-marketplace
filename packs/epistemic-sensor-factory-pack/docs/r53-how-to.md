# How-to — qualify a causal propagation edge

For each candidate edge, require an exact source consumer, a returned/replayable receipt, a downstream opportunity, temporal ordering, and an independent target evidence root. Record confidence explicitly and keep standing/authority transfer false.

Run:

```bash
python3 -m pytest -q packs/epistemic-sensor-factory-pack/tests/test_r53_static_contract.py packs/epistemic-sensor-factory-pack/tests/test_r53_causal_propagation.py
```

A missing causal or counterfactual witness is an observation gap, not permission to infer causality. Generated plans are SELECT/CONSTRUCT consequences and carry no DO authority.
