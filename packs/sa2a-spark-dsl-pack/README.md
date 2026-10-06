# sa2a-spark-dsl-pack

Spark DSL extension pack for AshA2A, revived from an empty husk (0.1.0 shipped
only `pack.toml` + a 73-line ontology with zero codegen). Version 0.2.0 models
the REAL landed compile-time surface as RDF:

- `ontology.ttl` — 237-line ontology modeling `BuildCapabilityIndex` (the
  transformer persisting flat `ash_a2a_*` keys with the SEC-04 consequence
  floor), `Verify`/`VerifySkills` verifiers with named refusal codes
  (`refused_action_not_found`, `refused_action_not_public`,
  `refused_argument_mapping_target`, `refused_type_not_json_serializable`,
  `refused_lease_required_no_authorizer`), grounded by per-individual file
  citations into the ash_a2a source.
- `templates/` — two Tera templates generating compiling `Spark.Dsl.Verifier`
  and `Spark.Dsl.Transformer` skeletons in the landed style, driven by the
  ontology.
- `queries/` — SPARQL extracting verifier refusal codes from the ontology.
- `gates/` — `010` completeness, `020` promise-vs-content, `030` projection
  consistency.

Domain-agnostic and composable across arbitrary Ash resources and domains.

## Standing

`ALIVE` (qualification/baseline.json, m14 dogfood FALSIFIER_PASS render +
m18 qualify_packs run, ggen 26.9.28). Zero consumers. Standing is scoped to
that qualification boundary — not a claim about any consumer.

## See Also

- [Pack contract](../../docs/reference/pack-contract.md)
- [Pack classes](../../docs/reference/pack-classes.md)
