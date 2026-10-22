#!/usr/bin/env python3
"""Semantic gate-witness court for industry-semantic-cad-bim.

For each gate (.rq) in gates/, run the SPARQL SELECT against
ontology.ttl + witnesses/pass/<stem>.ttl  -> expect ZERO rows (admit)
and against ontology.ttl + witnesses/fail/<stem>.ttl -> expect >= 1 row (refuse).

Fail-closed: any parse error, missing case, or wrong row count exits nonzero.
Chicago discipline: real rdflib engine, real graph state — no mocks.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from rdflib import Graph

PACK = Path(__file__).resolve().parent.parent


def load(path: Path) -> Graph:
    graph = Graph()
    graph.parse(path.as_posix(), format="turtle")
    return graph


def run_gate(gate_text: str, data: Graph) -> list[dict]:
    rows = data.query(gate_text)
    return [dict(row.asdict()) for row in rows]


def main() -> int:
    gates_dir = PACK / "gates"
    pass_dir = PACK / "witnesses/pass"
    fail_dir = PACK / "witnesses/fail"
    ontology = load(PACK / "ontology.ttl")

    gate_paths = sorted(gates_dir.glob("*.rq"))
    if not gate_paths:
        print("REFUSED:COURT:no gates found", file=sys.stderr)
        return 2

    results = []
    failures = []
    for gate_path in gate_paths:
        stem = gate_path.stem
        pass_path = pass_dir / f"{stem}.ttl"
        fail_path = fail_dir / f"{stem}.ttl"
        if not pass_path.exists() or not fail_path.exists():
            failures.append(f"{stem}: missing witness pair")
            continue
        gate_text = gate_path.read_text(encoding="utf-8")

        pass_graph = load(pass_path) + ontology
        pass_rows = run_gate(gate_text, pass_graph)
        fail_graph = load(fail_path) + ontology
        fail_rows = run_gate(gate_text, fail_graph)

        ok = (len(pass_rows) == 0) and (len(fail_rows) >= 1)
        results.append({
            "case": stem,
            "pass_rows": len(pass_rows),
            "fail_rows": len(fail_rows),
            "verdict": "PASS" if ok else "REFUSED",
        })
        if not ok:
            failures.append(
                f"{stem}: pass_rows={len(pass_rows)} (expect 0), "
                f"fail_rows={len(fail_rows)} (expect >=1)"
            )

    report = {
        "schema": "ggen.semantic-gate-witness-court/1",
        "pack": PACK.name,
        "cases": results,
        "standing": "REFUSED" if failures else "ALIVE",
    }
    print(json.dumps(report, indent=2))
    if failures:
        for failure in failures:
            print(f"REFUSED:GATE_WITNESS_COURT:{failure}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
