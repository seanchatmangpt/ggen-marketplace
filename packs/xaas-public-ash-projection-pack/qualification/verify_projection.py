#!/usr/bin/env python3
"""Repository-native semantic projection court."""
from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
CASES = (
    ("020_projection_identity.rq", "020_projection_identity.ttl"),
    ("030_projection_collision.rq", "030_projection_collision.ttl"),
)

def rows(gate, witness):
    graph = Graph()
    graph.parse(witness, format="turtle")
    return list(graph.query((ROOT / "gates" / gate).read_text()))

def main():
    for gate, fixture in CASES:
        passed = rows(gate, ROOT / "witnesses" / "pass" / fixture)
        failed = rows(gate, ROOT / "witnesses" / "fail" / fixture)
        assert passed == [], (gate, "pass produced violations", passed)
        assert failed != [], (gate, "negative did not falsify")
    print("ALIVE xaas-public-ash projection court: 2/2")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
