#!/usr/bin/env python3
"""Irreducible SPARQL-engine adapter: execute every R43 sensor on the grounded fixture."""
from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
graph = Graph()
graph.parse(ROOT / "ontology.ttl", format="turtle")
graph.parse(ROOT / "fixtures" / "r43-reference.ttl", format="turtle")

queries = sorted((ROOT / "queries").glob("*.rq"))
failures = []
for query_path in queries:
    try:
        list(graph.query(query_path.read_text()))
    except Exception as exc:  # permanent court prints exact failed sensor
        failures.append((query_path.name, type(exc).__name__, str(exc)))

if failures:
    for failure in failures:
        print("FAIL", *failure)
    raise SystemExit(1)
print(f"R43 executable sensor court: PASS ({len(queries)}/{len(queries)})")
