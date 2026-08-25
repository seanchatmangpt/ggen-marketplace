# How to extend the rebloom frontier

1. Represent each newly qualified capability as RDF with reversibility, expected reuse, and capability-space delta.
2. Add composition candidates that reference two or more admitted capabilities.
3. Keep `grantsDoAuthority=false`; this pack never crosses BRCE.
4. Raise `maxDepth` or `maxOrder` only with a corresponding falsifier proving termination and bounded cost.
5. Regenerate twice and compare outputs byte-for-byte before consumer qualification.
6. Run the fail-closed gate on every projected plan and retain the receipt with the candidate identity.
