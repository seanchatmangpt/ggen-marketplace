# Qualification — delegation-admission-pack 0.1.0

## Court

The pack is admitted by violation-row SELECT gates. Qualification must run the
pack ontology and positive fixture as clean graphs, then run the negative fixture
and require the intended gates to fire.

Expected anti-vacuity contract:

| graph | 010 | 015 | 020 | 030 | 040 | 050 |
|---|---:|---:|---:|---:|---:|---:|
| ontology.ttl | 0 | 0 | 0 | 0 | 0 | 0 |
| pos_admitted.ttl | 0 | 0 | 0 | 0 | 0 | 0 |
| neg_capacity_and_independence.ttl | 0 | 0 | >=1 | >=1 | 0 | 0 |

A result outside that matrix is a pack failure. The negative fixture is deliberately
otherwise complete so its rows cannot be explained by unrelated missing evidence.

## Marketplace admission

Run from repository root:

```bash
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py catalog > /tmp/catalog-a.json
python3 scripts/marketplace.py catalog > /tmp/catalog-b.json
cmp /tmp/catalog-a.json /tmp/catalog-b.json
```

The pack itself grants no runtime authority. Marketplace validation establishes only
manifest/RDF/gate structural admission; consumer execution and BRCE standing remain
separate evidence.
