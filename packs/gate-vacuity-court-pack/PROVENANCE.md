# PROVENANCE — gate-vacuity-court-pack

Every fact in `ontology.ttl` was produced by really executing `ggen 26.8.28`
(`~/.local/bin/ggen`) on 2026-09-06 against the real
`/Users/sac/ggen-marketplace/packs` tree. Nothing here is inferred from a pack
name, a README, or a field name.

## Authority boundary

This pack carries **no runtime actuation authority**. Both generated artifacts
are observers:

- `src/gate_vacuity_court.py` reads `ggen.toml` and `gates/*.rq` and prints a
  report. It never writes to a pack, never repairs, never publishes, and exits
  0 regardless of verdict — refusal authority stays with GymAct/BRCE admission.
- `tests/executable_gate_falsifier.py` runs `ggen sync run` only inside a
  `tempfile.TemporaryDirectory()` copy. The source pack is never mutated.

## The load-bearing observation

`ggen 26.8.28` loads SPARQL gates **only** from the `ggen.toml` key
`[validation] gates = [...]`. A `gates/*.rq` file present on disk but absent
from that list is never read and therefore can never refuse.

Verified by a two-arm experiment on `automatic-autonomic-operations-pack`
(`gate_vacuity_experiment.sh`), both arms on an ontology with all 16
`aa:falsifier` triples removed — exactly the condition `gates/010_required.rq`
exists to catch:

```text
=== A) AS SHIPPED: gates/010_required.rq exists, ggen.toml has no [validation] ===
  mutation: aa:falsifier triples 16 -> 0
  [validation] blocks in ggen.toml: 0
  EXIT_A=0
  generated files:
    consumer/automatic-autonomic-operations/RELEASE_STANDING.json
    consumer/automatic-autonomic-operations/Cargo.toml
    ... (8 files written despite the violation)

=== B) SAME mutated ontology, gate WIRED via [validation] ===
  mutation: aa:falsifier triples 16 -> 0
  [validation] blocks in ggen.toml: 1
  EXIT_B=1
  ERROR: ... validation error: [FM-LAW-018] SPARQL gate `gates/010_required.rq`
  refused the sync: SELECT returned 15 row(s); first row:
  { ?capability = https://ggen.dev/ontology/automatic-autonomic#KnowledgeHookEmission }
  generated files: (none)
```

The gate query is correct. It simply was never loaded.

## Census (real run of the generated auditor, 2026-09-06)

```text
== gate-vacuity court over /Users/sac/ggen-marketplace/packs (ggen 26.8.28) ==
  packs=229 with_manifest=94 shipping_rq_gates=151 wiring_validation_gates=2
  VACUOUS_GATE=149 VACUOUS_LAW=3 NOT_CONSUMABLE=135
```

`VACUOUS_LAW` is `[law] rules = []` — an empty rule list that enforces nothing:
`ash-reactor-domain-error-contract-pack`,
`forced-top25-admissibility-factory-pack`,
`forced-top25-ocel-fanout-meta-pack`.

## Vocabulary reuse

`dqv:` (Metric/Dimension) carries the quality-measurement shape, `prov:Entity`
+ `prov:wasDerivedFrom` the census lineage, `dcterms:` description/conformsTo,
`skos:notation` the refusal codes. Only the ggen-specific manifest keys and
court checks are minted under `gvc:`, because no public vocabulary models a
`ggen.toml` key.

## Reproduce

```bash
cd <this pack>
ggen sync run                                    # writes src/ and tests/
python3 src/gate_vacuity_court.py /Users/sac/ggen-marketplace/packs
python3 tests/executable_gate_falsifier.py \
    /Users/sac/ggen-marketplace/packs/automatic-autonomic-operations-pack \
    010_required.rq aa:falsifier
```
