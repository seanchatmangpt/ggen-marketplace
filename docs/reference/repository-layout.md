# Reference: repository layout

| Path | Contract |
|---|---|
| `packs/` | Canonical reusable pack corpus. |
| `packs/<name>/pack.toml` | Pack identity and description. |
| `packs/<name>/ontology.ttl` | Pack RDF source. |
| `packs/<name>/templates/` | One or more `.tmpl` projection templates. |
| `packs/<name>/gates/` | Optional `.rq` native SPARQL gates and `.py` pack-owned verifier gates. |
| `scripts/marketplace.py` | Local-first structural validator, derived catalog, and fingerprint. |
| `docs/tutorials/` | Learning-oriented Diátaxis quadrant. |
| `docs/how-to/` | Task-oriented Diátaxis quadrant. |
| `docs/reference/` | Contract/reference Diátaxis quadrant. |
| `docs/explanation/` | Understanding-oriented Diátaxis quadrant. |
| `.github/workflows/ci.yml` | Read-only wrapper around local acceptance. |
| `.ggen-packs-source-sha` | Initial source-commit receipt; historical, not a moving pointer. |
