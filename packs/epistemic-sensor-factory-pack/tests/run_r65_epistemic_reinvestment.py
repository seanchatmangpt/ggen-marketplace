#!/usr/bin/env python3
from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
g = Graph()
g.parse(ROOT / "ontology.ttl", format="turtle")
g.parse(ROOT / "ontology.r65-epistemic-reinvestment.ttl", format="turtle")
g.parse(ROOT / "fixtures/r65-epistemic-reinvestment.ttl", format="turtle")
queries = []
ordinals = set()
for p in sorted((ROOT / "queries").glob("*_r65_*.rq")):
    try:
        number = int(p.name.split("_", 1)[0])
    except ValueError:
        continue
    if 1401 <= number <= 1450:
        queries.append(p)
        ordinals.add(number)

# R65's canonical contract is ordinal coverage, not global file cardinality.
# Later lawful extensions may add additional courts within an ordinal without
# invalidating the original 50-sensor family. Refuse gaps, not composition.
expected_ordinals = set(range(1401, 1451))
assert ordinals == expected_ordinals, sorted(expected_ordinals - ordinals)
assert len(queries) >= len(expected_ordinals), len(queries)
for q in queries:
    list(g.query(q.read_text()))
assert not any("odrl:execute" in q.read_text() for q in queries)
print(
    f"R65 ALIVE: canonical_ordinals={len(expected_ordinals)}/50 "
    f"executable_courts={len(queries)} triples={len(g)} consequential_do=false"
)
