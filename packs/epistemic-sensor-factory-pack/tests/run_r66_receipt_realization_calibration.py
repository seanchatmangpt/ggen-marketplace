#!/usr/bin/env python3
from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
g = Graph()
g.parse(ROOT / "ontology.ttl", format="turtle")
g.parse(ROOT / "ontology.r61-consumer-receipt-assimilation.ttl", format="turtle")
g.parse(ROOT / "ontology.r65-epistemic-reinvestment.ttl", format="turtle")
g.parse(ROOT / "ontology.r66-receipt-realization-calibration.ttl", format="turtle")
g.parse(ROOT / "fixtures/r66-receipt-realization-calibration.ttl", format="turtle")
queries = []
for p in sorted((ROOT / "queries").glob("*_r66_*.rq")):
    try:
        number = int(p.name.split("_", 1)[0])
    except ValueError:
        continue
    if 1452 <= number <= 1501:
        queries.append(p)
assert len(queries) == 50, len(queries)
results = {}
for q in queries:
    results[q.name] = list(g.query(q.read_text()))
assert len(results["1452_r66_consumer_subject_census.rq"]) == 1
assert len(results["1496_r66_1000x_admission.rq"]) == 0, "reference fixture must not falsely admit 1000X"
assert len(results["1497_r66_clean_independent_consumers.rq"]) == 1
assert not any("odrl:execute" in q.read_text() for q in queries)
print(f"R66 ALIVE: {len(queries)}/50 sensors executed; triples={len(g)}; 1000x=NOT_ADMITTED; consequential_do=false")
