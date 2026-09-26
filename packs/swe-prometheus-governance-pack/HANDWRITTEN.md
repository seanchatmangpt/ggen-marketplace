# HANDWRITTEN.md — swe-prometheus-governance-pack

This pack's authored surface is intentionally small. Consumers should project
the case JSON; they should not hand-copy the six-dimension contract.

| path | role | why authored once |
|---|---|---|
| `pack.toml` | pack admission/authority boundary | marketplace source record |
| `ontology.ttl` | public-vocabulary-anchored paired evidence model | failed edge is SWE-Prometheus-specific semantics |
| `gates/010_exact_identity.rq` | exact-subject guard | one graph = one base/patch subject |
| `gates/020_dimension_universe.rq` | D1..D6 closed universe | prevents missing/duplicate dimension drift |
| `gates/030_detected_requires_mutation_receipt.rq` | gate-strength evidence guard | detected is evidence, not a string claim |
| `gates/040_paired_score_shape.rq` | score/evidence guard | configuration presence cannot masquerade as paired evidence |
| `templates/case.json.tmpl` | generated autofde-lab court input | consumer projection; generated output must not be hand-edited |
| `qualification/fixtures/*.ttl` | anti-vacuity witnesses | permanent positive/negative falsifiers |
| `QUALIFICATION.md` | evidence ledger | records observed vs unsupported verification |

Generated consumer files are projections and should be regenerated from RDF
rather than edited manually.
