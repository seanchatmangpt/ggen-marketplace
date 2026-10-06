# sa2a-chicago-court-pack

SPARQL-driven Chicago adversarial court suite generator, rebuilt on the REAL
ash_a2a court machinery (SA2A-B5 authority/BRCE dispatch path, SA2A-B11 wire
path, the authority harness, and the independent-postcondition court).
Version 0.2.0, project profile (`ggen.toml` generation contract), 446-line
`ontology.ttl`, 7 SPARQL/shell gates (`gates/000`–`060`), and a committed
generated output (`generated/chicago_court_suite_test.exs`). Generates an
ExUnit court suite (setup/teardown over real collaborators, a positive control
plus a kill per court, Chicago zero-mock rules) bound to the consumer's
resource/skill names via `chi:SuiteConfig` — templates never hardcode module
names.

## Standing

`ALIVE` (qualification/baseline.json, m14 dogfood FALSIFIER_PASS render +
m18 qualify_packs run, ggen 26.9.28). Zero consumers. Standing is scoped to
that qualification boundary — not a claim about any consumer.

## See Also

- [Pack contract](../../docs/reference/pack-contract.md)
- [Pack classes](../../docs/reference/pack-classes.md)
