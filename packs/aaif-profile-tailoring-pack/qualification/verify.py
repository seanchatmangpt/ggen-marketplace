#!/usr/bin/env python3
"""Gate-witness court: run each gate against its same-stem witnesses.

pass witness => 0 rows (exit 0); fail witness => >= 1 row (exit 0).
Any violation exits 2.
"""
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
        pass_witness = PACK / "witnesses" / "pass" / f"{gate.stem}.ttl"
        fail_witness = PACK / "witnesses" / "fail" / f"{gate.stem}.ttl"
        if not pass_witness.exists() or not fail_witness.exists():
            failures.append(f"{gate.stem}: missing same-stem witness pair")
            continue
        p = rows(gate, pass_witness)
        f = rows(gate, fail_witness)
        cases.append({"gate": gate.stem, "pass_rows": p, "fail_rows": f})
        if p != 0:
            failures.append(f"{gate.stem}: pass witness refused ({p} rows)")
        if f == 0:
            failures.append(f"{gate.stem}: fail witness admitted (vacuous gate)")
    print(json.dumps({"cases": cases, "failures": failures}, indent=2))
    return 2 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
