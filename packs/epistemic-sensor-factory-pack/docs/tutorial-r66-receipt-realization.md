# Tutorial: calibrate independent consumer realization

Use R66 when a canonical capability has predicted consumer fanout but only some consumers have returned exact, independently rooted receipts.

1. Materialize exact consumer subjects as repository + SHA evidence.
2. Bind returned receipts to their producer head and evidence root.
3. Execute sensors `1452`–`1501` against the admitted RDF graph.
4. Inspect fanout, receipt-return, assimilation, dependency-relief, and opportunity-yield calibration.
5. Treat `1496` as the 1000X admission boundary: an empty result means NOT_ADMITTED, not failure.
6. Generate the R66 calibration projection through ggen; never edit the generated JSON.

The reference fixture intentionally has two realized consumers but only one independent evidence root. It therefore demonstrates partial realization without fabricating a portfolio crown.
