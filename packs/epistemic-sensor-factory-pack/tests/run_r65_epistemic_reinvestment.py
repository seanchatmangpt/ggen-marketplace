#!/usr/bin/env python3
from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
g = Graph()
g.parse(ROOT / "ontology.ttl", format="turtle")
g.parse(ROOT / "ontology.r65-epistemic-reinvestment.ttl", format="turtle")
g.parse(ROOT / "fixtures/r65-epistemic-reinvestment.ttl", format="turtle")
queries = sorted((ROOT / "queries").glob("14[0-4][1-9]_r65_*.rq")) + sorted((ROOT / "queries").glob("1450_r65_*.rq"))
queries = [p for p in queries if 1401 <= int(p.name.split('_',1)[0]) <= 1450]
assert len(queries) == 50, len(queries)
for q in queries:
    list(g.query(q.read_text()))
assert not any("odrl:execute" in q.read_text() for q in queries)
print(f"R65 ALIVE: {len(queries)}/50 sensors executed; triples={len(g)}; consequential_do=false")
