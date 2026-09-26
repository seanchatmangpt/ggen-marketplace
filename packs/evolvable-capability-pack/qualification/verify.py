#!/usr/bin/env python3
"""Executable anti-vacuity court for evolvable-capability-pack."""

from __future__ import annotations

import json
from pathlib import Path

from rdflib import Graph

PACK = Path(__file__).resolve().parents[1]
GATES = PACK / "gates"
PASS = PACK / "witnesses" / "pass"
FAIL = PACK / "witnesses" / "fail"
ONTOLOGY = PACK / "ontology.ttl"


def execute(gate: Path, witness: Path) -> int:
    graph = Graph()
    graph.parse(ONTOLOGY, format="turtle")
    graph.parse(witness, format="turtle")
    return len(list(graph.query(gate.read_text(encoding="utf-8"))))


def main() -> int:
    results: list[dict[str, object]] = []
    refused = False

    for gate in sorted(GATES.glob("*.rq")):
        positive = PASS / f"{gate.stem}.ttl"
        negative = FAIL / f"{gate.stem}.ttl"
        if not positive.is_file() or not negative.is_file():
            print(f"REFUSED:MISSING_WITNESS:{gate.stem}")
            refused = True
            continue

        pass_rows = execute(gate, positive)
        fail_rows = execute(gate, negative)
        case_ok = pass_rows == 0 and fail_rows > 0
        refused = refused or not case_ok
        results.append(
            {
                "gate": gate.name,
                "pass_rows": pass_rows,
                "fail_rows": fail_rows,
                "standing": "ALIVE" if case_ok else "REFUSED",
            }
        )

    payload = {
        "pack": PACK.name,
        "case_count": len(results),
        "cases": results,
        "standing": "REFUSED" if refused else "ALIVE",
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 2 if refused else 0


if __name__ == "__main__":
    raise SystemExit(main())
