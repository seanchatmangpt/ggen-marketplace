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

## Full end-to-end lifecycle (real ggen, real registry)

`scripts/e2e-lifecycle-test.sh` exercises the whole marketplace lifecycle for real: the
`marketplace.py` CLI (`validate`/`catalog`), a real HTTP fetch of the live published registry
index and pack archive with digest verification against the actual downloaded bytes, a fresh
consumer composing `clap-noun-verb-zeroconfig-pack`'s fetched content with
`chicago-tdd-tools-pack`, a real `ggen sync run`, and `cargo build`/`cargo test` — including
generated `CliHarness` boundary tests that spawn the real compiled binary (no mocks anywhere in
the chain). Requires the `ggen` binary and network access to `github.com`:

```bash
bash scripts/e2e-lifecycle-test.sh
```
