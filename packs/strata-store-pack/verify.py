#!/usr/bin/env python3
"""Real Chicago verifier: re-run every gates/*.rq SELECT against ontology.ttl.
Exit 0 iff every gate returns zero rows (violation-free); else print and exit 1.
(Chicago pattern shared with strata-pn64-pack/verify.py — no mocks, real graph,
real query execution; the gate .rq files are the only authority.)
"""
import sys
from pathlib import Path

from typing import Iterable, cast

from rdflib import Graph

PACK_DIR = Path(__file__).resolve().parent


def main() -> int:
    graph = Graph()
    graph.parse(PACK_DIR / "ontology.ttl", format="turtle")

    violations = 0
    for gate in sorted((PACK_DIR / "gates").glob("*.rq")):
        query = gate.read_text(encoding="utf-8")
        # rdflib types Result.__iter__ as Iterator[Union[_TripleType, bool,
        # ResultRow]]; SELECT rows are always iterable tuples, so narrow via cast.
        rows = list(cast(Iterable[tuple], graph.query(query)))
        if rows:
            violations += 1
            print(f"VIOLATION {gate.name}: {len(rows)} row(s)")
            for row in rows:
                print("  " + "; ".join(str(c) for c in row))
        else:
            print(f"PASS {gate.name}: 0 rows")

    if violations:
        print(f"FAIL: {violations} gate(s) with violations")
        return 1
    print("OK: all gates zero-rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
