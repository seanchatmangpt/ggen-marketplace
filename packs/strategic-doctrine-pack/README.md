# strategic-doctrine-pack

Canonical strategic-doctrine graph for the strategic compiler (v26.9.25 lane 1).
It is read by napoleon.berthier (campaign compiler), the ggen_igniter
doctrine-hddl-pack, and the autofde-lab boundary lab. Each consumer pins a copy
of this graph plus a sha256 check and does not redefine it.

- IRI: `https://ggen.dev/ontology/strategic-doctrine#`
- Turtle prefix: `sd:`. `33s:` is not a legal PN_PREFIX because it starts
  with a digit, so "33S" is a display name only.
- Authority: `NONE`. Ceiling: `SELECT`/`CONSTRUCT`. Never `DO`.

## Layout

| path | role |
|---|---|
| `ontology.ttl` | classes, properties, the 14-operator primitive algebra, the catalog authority record, and the licensing `cs:NonClaim` |
| `ontology/world-model.ttl` | alignments only: Actor ⊑ org:Organization, prov:Agent; Market ⊑ schema:Product; Step ⊑ prov:Activity; FalsifierObservation ⊑ sosa:Observation; Timing ⊑ time:Interval; also the observable properties |
| `ontology/doctrine-33.ttl` | the 33 entries: 6 operationalized `sd:Strategy` (11 14 17 22 23 27), 27 `sd:StrategyStub` |
| `ontology/shapes.ttl` | SHACL shapes |
| `gates/010..060` | fail-closed SPARQL gates. Any returned row is a refusal. |
| `witnesses/{pass,fail}` | exact-stem witness pairs, one per gate |
| `gate-court.toml`, `runners/semantic_runner.py` | gate-witness court. The runner is adapted from `semantic-case-study-pack`. |
| `fixtures/entrant-world.ttl` | Acme, a 12-person software company, plus 3 incumbents. Contains SOSA observations and 4 candidate applicabilities. |
| `queries/admitted_applicability.rq` | admits a candidate only if all of its strategy's conditions hold. On the fixture it admits 3 of the 4. |
| `generated/catalog.json` | deterministic projection (ordinal, id, title, primitives, falsifiers). Never hand-edited. |
| `scripts/project_catalog.py` | regenerates the catalog; `--check` refuses a stale projection |
| `sources/vendor/` | vendored copies of the public vocabularies, each with a `receipt.json`, plus `materialization-receipt.json` |

## Primitive algebra

The 14 operators are: shape, probe, conceal, reveal, concentrate, disperse,
delay, accelerate, commit, withdraw, divide, combine, substitute, transform.

They form five dual pairs, and `sd:dualOf` is asserted in both directions:

- conceal/reveal
- concentrate/disperse
- delay/accelerate
- commit/withdraw
- divide/combine

## Gates

| gate | refuses |
|---|---|
| 010 strategy_requires_falsifier | an operationalized strategy with no typed falsifier that states what refutes it |
| 020 applicability_public_class_only | a condition over a class outside ORG/PROV/schema.org/SOSA/SSN/Time/`sd:` |
| 030 composition_known_primitive | a step whose operator is outside the 14, or that has no operator |
| 040 step_order_total | step orders that are missing, duplicated, non-integer, or not exactly 1..n |
| 050 no_excerpt | a literal over 60 characters on a strategy node, or any `sd:quote` |
| 060 licensing_nonclaim_present | a catalog entry with no complete `cs:NonClaim` |

## Licensing boundary

The catalog is this marketplace's own operationalization. It is indexed by the
ordinal sequence of *The 33 Strategies of War* (R. Greene, 2006).

The catalog is **not licensed** from the author or publisher and carries **no
endorsement** by them. It reproduces **no text** of the work.

Each entry holds only:

- an ordinal;
- an own paraphrased title of at most 60 characters;
- an own composition of primitive operators.

The alignment between ordinals and the work's sequence is best-effort. It has
not been verified against a licensed copy.

The `sd:nonclaim-licensing` individual states this boundary in the graph, and
gate 060 refuses any graph that lacks it.

## Public ontologies

Vendored under `sources/vendor/`, copied byte-for-byte from `ontologies/public/`
with a sha256 recorded per file:

- PROV-O
- SOSA
- SSN
- OWL-Time
- ORG
- schema.org

**Not vendored:** GeoSPARQL and the OCEL 2.0 ontology. Neither is present in
`ontologies/public/`, and nothing in this pack depends on them.

## Verify

```bash
python3 scripts/marketplace.py validate
python3 packs/strategic-doctrine-pack/scripts/project_catalog.py --check
python3 -m pytest tests/test_strategic_doctrine_pack.py -q
python3 scripts/check_gate_witness_courts.py
```
