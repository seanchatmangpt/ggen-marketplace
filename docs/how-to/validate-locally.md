# How to validate locally

Use Python 3.11 or newer; the validator uses the standard-library `tomllib` parser.

```bash
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py catalog > /tmp/catalog-a.json
python3 scripts/marketplace.py catalog > /tmp/catalog-b.json
cmp /tmp/catalog-a.json /tmp/catalog-b.json
python3 scripts/marketplace.py fingerprint
```

`validate` checks the repository and Diátaxis contract. `catalog` emits a deterministic JSON projection. `fingerprint` computes a content fingerprint over admitted pack files.

A `REFUSED:*` result is an acceptance failure, not a warning to ignore. Marketplace validation does not execute ggen; use the runtime for behavioral evidence.
