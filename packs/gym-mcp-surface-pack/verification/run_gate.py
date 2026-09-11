#!/usr/bin/env python3
"""Run the authority-boundary gate against a real graph. Any row refuses manufacture."""
import sys

import rdflib

graph_path, gate_path = sys.argv[1], sys.argv[2]
g = rdflib.Graph()
g.parse(graph_path, format="turtle")
rows = list(g.query(open(gate_path).read()))
print(f"graph={graph_path}")
print(f"  triples={len(g)}  refusal_rows={len(rows)}")
for r in rows[:12]:
    print(f"  REFUSE {r[0]} :: {r[1]}")
sys.exit(1 if rows else 0)
