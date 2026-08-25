#!/usr/bin/env python3
"""Irreducible SPARQL-engine adapter for the R45B replication-yield tranche."""
from pathlib import Path
import re
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
graph = Graph()
graph.parse(ROOT / "ontology.ttl", format="turtle")
graph.parse(ROOT / "fixtures" / "r45b-replication-yield.ttl", format="turtle")
queries = []
for path in sorted((ROOT / "queries").glob("*.rq")):
    match = re.match(r"^(\d{3})_", path.name)
    if match and 136 <= int(match.group(1)) <= 185:
        queries.append(path)
assert len(queries) == 50, f"R45B must contain exactly 50 sensors, got {len(queries)}"
failures = []
for path in queries:
    try:
        list(graph.query(path.read_text()))
    except Exception as exc:
        failures.append((path.name, type(exc).__name__, str(exc)))
if failures:
    for failure in failures:
        print("FAIL", *failure)
    raise SystemExit(1)
print("R45B replication-yield court: PASS (50/50)")
