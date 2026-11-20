# smalt-substrate-pack Standing

Standing: VERIFIED / ALIVE

Tip re-court 2026-11-20 (ggen 26.11.5, subject `7ad4b6db`). See
`docs/jira/v26.11.20/receipts/sj-pack-sourced-completion-marketplace-not-blocker.md`.

| Court | EXIT / result |
|---|---|
| `ggen graph validate --files ontology.ttl --shapes shapes/smalt-shapes.ttl` | **0** (`shapes_conform: true`, 2354 quads) |
| rdflib gates `config_coverage` + `shapes-coverage` | **0** rows each |
| rdflib `verify/*.unbound.rq` + `api_admission.rq` | **0** rows each |
| mutation FLIP (ConfigKey census-empty; drop apiVersion) | **FLIP** |
| `qualify_packs.py --pack smalt-substrate-pack` | **ALIVE** (terraform root verified) |

Marketplace is not the SJ finish blocker for this pack.
