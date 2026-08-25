# How to select realized-capital reinvestment candidates

1. Start only from R64 `ProductionFunctionObservation` subjects with exact standing and receipts.
2. Require positive frontier delta, non-zero downstream opportunity yield, and non-zero reusable capability yield.
3. Require replay verification, at least two independent evidence roots, and at least three factor-evidence observations.
4. Inspect observation, reuse, and opportunity factors independently before using their product.
5. Prefer cross-repository candidates and underrepresented repository families when other evidence is non-dominated.
6. Preserve all non-dominated candidates; rankings are SELECT surfaces only.
7. Execute `python3 packs/epistemic-sensor-factory-pack/tests/run_r65_realized_capital_reinvestment.py` before admission.
