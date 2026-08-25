#!/usr/bin/env python3
"""Irreducible SPARQL-engine adapter: execute the immutable R43 001..050 court."""
from pathlib import Path
import re
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
graph = Graph()
graph.parse(ROOT / "ontology.ttl", format="turtle")
graph.parse(ROOT / "fixtures" / "r43-reference.ttl", format="turtle")

queries = []
for path in sorted((ROOT / "queries").glob("*.rq")):
    match = re.match(r"^(\d{3})_", path.name)
    if match and 1 <= int(match.group(1)) <= 50:
        queries.append(path)
assert len(queries) == 50, f"R43 baseline must contain exactly 50 sensors, got {len(queries)}"

failures = []
for query_path in queries:
    try:
        list(graph.query(query_path.read_text()))
    except Exception as exc:
        failures.append((query_path.name, type(exc).__name__, str(exc)))

if failures:
    for failure in failures:
        print("FAIL", *failure)
    raise SystemExit(1)
print("R43 executable sensor court: PASS (50/50 immutable baseline)")
