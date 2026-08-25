# How to run R66 receipt-realization calibration

Run the permanent court after adding or refreshing exact consumer evidence:

```bash
python3 packs/epistemic-sensor-factory-pack/tests/run_r66_receipt_realization_calibration.py
```

For each consumer, provide exact repository and SHA, qualification/containment/replay evidence, standing freshness, producer head, and evidence-root independence. Returned receipts that have not yet been assimilated must remain visible as an assimilation gap.

Interpretation rules:

- a missing SHA is an identity falsifier;
- producer-local evidence is not an independent root;
- stale standing is not current standing;
- `1000X` is admitted only by sensor 1496 from observed factors;
- consequential DO is prohibited in this measurement family.
