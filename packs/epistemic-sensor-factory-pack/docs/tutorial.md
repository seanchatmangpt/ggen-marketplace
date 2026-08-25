# Tutorial: manufacture a Better-Eyes sensor family

1. Model the observable class as `esf:SensorFamilySpec` in `ontology.ttl`.
2. Add `esf:SensorSpec` facts for each independently meaningful metric, query pattern, and opportunity kind.
3. Run ggen from the pack root; the generated plan is a consequence, not an editing surface.
4. Qualify the pack contract and the generated consequence before consuming it in a portfolio adapter.
5. Preserve exact subject identity and evidence roots; this pack has no ambient DO authority.
