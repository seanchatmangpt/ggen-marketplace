#!/usr/bin/env python3
"""Chicago verifier for industry-pharma-21cfr.

1. Pack graph: every gate/*.rq must return ZERO rows over ontology.ttl
   (the ontology carries a fully compliant individual chain).
2. Non-vacuity court (exactly-one-law): for each gate stem, the PASS witness
   must produce ZERO rows from EVERY gate, and the FAIL witness must produce
   >= 1 row ON ITS OWN GATE and ZERO rows from every OTHER gate — a fail
   witness that flips a second law is a cross-contaminated court, not a pass.
Exit 0 iff all of the above hold; else print the failing legs and exit 1.
"""
import sys
from pathlib import Path
from typing import Iterable, cast

from rdflib import Graph

PACK = Path(__file__).resolve().parent.parent


def rows(graph: Graph, gate: Path) -> list[tuple]:
    return list(cast(Iterable[tuple], graph.query(gate.read_text(encoding="utf-8"))))


def main() -> int:
    gates = sorted((PACK / "gates").glob("*.rq"))
    if not gates:
        print("FAIL: no gates")
        return 1

    failures: list[str] = []

    graph = Graph()
    graph.parse(PACK / "ontology.ttl", format="turtle")
    for gate in gates:
        found = rows(graph, gate)
        if found:
            failures.append(f"ontology {gate.name}: {len(found)} violation row(s) over the pack graph")
        else:
            print(f"PASS ontology {gate.name}: 0 rows")

    for gate in gates:
        for polarity, expect_violation in (("pass", False), ("fail", True)):
            witness = PACK / "witnesses" / polarity / f"{gate.stem}.ttl"
            if not witness.exists():
                failures.append(f"{gate.stem}: missing {polarity} witness")
                continue
            wg = Graph()
            wg.parse(witness, format="turtle")
            per_gate = {g.stem: len(rows(wg, g)) for g in gates}
            if expect_violation:
                if per_gate[gate.stem] == 0:
                    failures.append(f"{gate.stem}: FAIL witness did not flip its gate (VACUOUS)")
                elif any(n for s, n in per_gate.items() if s != gate.stem):
                    flipped = sorted(s for s, n in per_gate.items() if n and s != gate.stem)
                    failures.append(f"{gate.stem}: FAIL witness flips other gates {flipped} (NOT exactly-one-law)")
                else:
                    print(f"PASS court {gate.stem}: fail witness flips ONLY its gate "
                          f"({per_gate[gate.stem]} row(s))")
            else:
                if any(per_gate.values()):
                    flipped = sorted(s for s, n in per_gate.items() if n)
                    failures.append(f"{gate.stem}: PASS witness flips {flipped}")
                else:
                    print(f"PASS court {gate.stem}: pass witness clean across all {len(gates)} gates")

    if failures:
        for line in failures:
            print(f"VIOLATION {line}")
        print(f"FAIL: {len(failures)} court leg(s)")
        return 1
    print(f"OK: {len(gates)} gates, {2 * len(gates)} witness legs, "
          "zero-rows/flips-as-contracted, exactly-one-law enforced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
