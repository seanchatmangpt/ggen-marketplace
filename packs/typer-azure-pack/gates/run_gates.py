#!/usr/bin/env python3
"""G14 gate runner: exit-checked SPARQL gates over ontology.ttl.

Each gates/*.rq (or *.rq beside the runner) is a SELECT gate: zero rows =
pass, any row = refusal (exit 1, rows printed). Anti-vacuity is proven by
the mutation court in docs/jira/v26.11.5/receipts/G14.md.
"""
import glob
import os
import sys

from rdflib import Graph

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    patterns = [os.path.join(here, "*.rq")]
    if os.path.basename(here) == "gates":
        patterns.insert(0, os.path.join(here, "gates", "*.rq"))
    paths = sorted(set(sum((glob.glob(p) for p in patterns), [])))
    onto = os.path.join(here, "..", "ontology.ttl")
    if not os.path.exists(onto):
        onto = os.path.join(here, "ontology.ttl")
    g = Graph()
    g.parse(onto, format="turtle")
    failures = []
    for path in paths:
        rows = list(g.query(open(path).read()))
        status = "PASS" if not rows else "FAIL"
        print(f"{os.path.relpath(path)}: {status} ({len(rows)} rows)")
        for row in rows:
            print("   ", tuple(str(x) for x in row))
        if rows:
            failures.append(path)
    if failures:
        print("GATE_REFUSAL: " + ", ".join(failures))
        return 1
    print("ALL_GATES_PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
