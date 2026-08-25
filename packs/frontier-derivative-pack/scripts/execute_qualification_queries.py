#!/usr/bin/env python3
from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
QUERY_DIR = ROOT / "qualification_queries"
queries = sorted(QUERY_DIR.glob("*.rq"))
if len(queries) != 50:
    raise SystemExit(f"REFUSED[R44_QUALIFICATION_SURFACE_COUNT]: expected=50 actual={len(queries)}")

graph = Graph()
graph.parse(ROOT / "ontology.ttl", format="turtle")

executed = []
for path in queries:
    text = path.read_text()
    if "SELECT" not in text.upper():
        raise SystemExit(f"REFUSED[NON_SELECT_QUALIFICATION]: {path.name}")
    result = graph.query(text)
    list(result)
    executed.append(path.name)

print(f"R44 frontier derivative qualification: PASS queries={len(executed)} triples={len(graph)}")
