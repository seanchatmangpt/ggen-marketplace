#!/usr/bin/env python3
"""Uniform exact-stem witness court for capability-ecology-pack.

One algorithm for all 10 family modules: for every gate in gates/, the union
ontology (ontology/*.ttl) plus its witnesses/pass/<stem>.ttl must yield zero
rows, and the union ontology plus witnesses/fail/<stem>.ttl must yield at
least one row. Exit 0 = ADMITTED, nonzero = REFUSED. Stdlib + rdflib only;
no network, no subprocess, no actuation.

Also exposes the module API the family tests drive directly:
gates(), load_graph(path), refusing_gates(graph).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from rdflib import Graph
except ImportError as exc:  # pragma: no cover
    raise SystemExit("REFUSED:VERIFIER_UNAVAILABLE:rdflib") from exc

ROOT = Path(__file__).resolve().parents[1]
GATES = sorted((ROOT / "gates").glob("*.rq"), key=lambda p: p.name)
ONTOLOGIES = sorted((ROOT / "ontology").glob("*.ttl"), key=lambda p: p.name)
PASS = ROOT / "witnesses/pass"
FAIL = ROOT / "witnesses/fail"
SCHEMA = "ggen.marketplace.capability-ecology-court/1"


def gates() -> list[Path]:
    return GATES


def base_graph() -> Graph:
    graph = Graph()
    for ontology in ONTOLOGIES:
        graph.parse(ontology, format="turtle")
    return graph


def load_graph(path: Path) -> Graph:
    graph = base_graph()
    graph.parse(path, format="turtle")
    return graph


def rows_for(graph: Graph, gate: Path) -> list[dict[str, str]]:
    results = graph.query(gate.read_text(encoding="utf-8"))
    return [{str(v): str(row[v]) for v in results.vars} for row in results]


def refusing_gates(graph: Graph) -> dict[str, list[dict[str, str]]]:
    refused: dict[str, list[dict[str, str]]] = {}
    for gate in GATES:
        rows = rows_for(graph, gate)
        if rows:
            refused[gate.name] = rows
    return refused


def main() -> int:
    failures: list[str] = []
    for gate in GATES:
        pass_witness = PASS / f"{gate.stem}.ttl"
        fail_witness = FAIL / f"{gate.stem}.ttl"
        if not pass_witness.is_file():
            failures.append(f"pass-witness-missing:{gate.stem}")
            continue
        if not fail_witness.is_file():
            failures.append(f"fail-witness-missing:{gate.stem}")
            continue
        pass_rows = rows_for(load_graph(pass_witness), gate)
        if pass_rows:
            failures.append(f"pass-witness-fired:{gate.stem}:{len(pass_rows)}rows")
        fail_rows = rows_for(load_graph(fail_witness), gate)
        if not fail_rows:
            failures.append(f"fail-witness-silent:{gate.stem}")
    report = {
        "schema": SCHEMA,
        "gate_count": len(GATES),
        "case_count": len(GATES),
        "failures": failures,
        "standing": "ALIVE" if not failures else "REFUSED",
    }
    print(json.dumps(report, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
