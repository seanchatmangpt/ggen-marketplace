#!/usr/bin/env python3
"""Run every gate against its same-stem witnesses: pass => zero rows, fail => >= 1 row."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from rdflib import Graph

PACK = Path(__file__).resolve().parents[1]


def rows(gate: Path, witness: Path) -> int:
    graph = Graph()
    graph.parse(witness, format="turtle")
    return len(list(graph.query(gate.read_text(encoding="utf-8"))))


def main() -> int:
    cases, failures = [], []
    for gate in sorted((PACK / "gates").glob("*.rq")):
        p = rows(gate, PACK / "witnesses" / "pass" / f"{gate.stem}.ttl")
        f = rows(gate, PACK / "witnesses" / "fail" / f"{gate.stem}.ttl")
        cases.append({"gate": gate.stem, "pass_rows": p, "fail_rows": f})
        if p != 0:
            failures.append(f"{gate.stem}: pass witness refused ({p} rows)")
        if f == 0:
            failures.append(f"{gate.stem}: fail witness admitted (vacuous gate)")
    print(json.dumps({"cases": cases, "failures": failures}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
