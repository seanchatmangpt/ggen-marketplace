# How to update a composition edge after qualification

1. Preserve the edge identity; do not delete a failed edge.
2. Append a realization with `prov:wasDerivedFrom`, exact subject, currentness, standing, observed delta, and receipt digest.
3. Increment the edge success or failure evidence only from a qualified receipt.
4. Keep expected delta and expected reuse independently observable from the posterior; calibration must not rewrite historical expectations.
5. Re-run all gates, manufacture the calibrated portfolio, and run the generated court.
6. Treat the output as SELECT/CONSTRUCT/VERIFY evidence only. Any DO transition requires a separate BRCE path and receipt.
