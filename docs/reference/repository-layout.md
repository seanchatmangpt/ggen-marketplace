# Reference: repository layout

| Path | Contract |
|---|---|
| `packs/` | Canonical admitted reusable pack corpus. |
| `packs/<name>/pack.toml` | Required identity; extension tables allowed. |
| `packs/<name>/*.ttl` | Root RDF sources, including conventional `ontology.ttl`. |
| `packs/<name>/ontology/**/*.ttl` | Optional split RDF source tree for project packs. |
| `packs/<name>/templates/` | Optional `.tmpl` / `.tera` projection templates. |
| `packs/<name>/gates/` | Optional `.rq` native gates and `.py` verifier gates. |
| `packs/<name>/ggen.toml` | Marks a self-contained project-profile pack. |
| `scripts/marketplace.py` | Local-first admission, derived catalog, and fingerprint. |
| `docs/tutorials/` | Learning-oriented Diátaxis quadrant. |
| `docs/how-to/` | Task-oriented Diátaxis quadrant. |
| `docs/reference/` | Contract/reference Diátaxis quadrant. |
| `docs/explanation/` | Understanding-oriented Diátaxis quadrant. |
| `.github/workflows/ci.yml` | Read-only wrapper around local acceptance. |
| `.ggen-packs-source-sha` | Historical initial source-commit receipt. |
