#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rdflib import Graph

PACK_ROOT = Path(__file__).resolve().parents[1]
GATES_DIR = PACK_ROOT / "gates"


def load_graph(path: Path) -> Graph:
    graph = Graph()
    graph.parse(path, format="turtle")
    return graph


def rows(gate: Path, graph: Graph) -> list:
    return list(graph.query(gate.read_text(encoding="utf-8")))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--witness", type=Path, required=True)
    parser.add_argument("--expectation", choices=("pass", "fail"), required=True)
    args = parser.parse_args()

    gate = args.gate.resolve()
    witness = args.witness.resolve()
    gates = sorted(GATES_DIR.glob("*.rq"))
    if not gate.is_file() or not witness.is_file() or not gates:
        print(
            json.dumps(
                {
                    "refusal": "REFUSED_STRUCTURAL",
                    "gate": str(gate),
                    "witness": str(witness),
                }
            ),
            file=sys.stderr,
        )
        return 3

    try:
        graph = load_graph(witness)
        observed = {candidate.stem: rows(candidate, graph) for candidate in gates}
    except Exception as error:
        print(
            json.dumps(
                {
                    "refusal": "REFUSED_RUNNER_ERROR",
                    "error": type(error).__name__,
                    "detail": str(error),
                }
            ),
            file=sys.stderr,
        )
        return 3

    firing = {
        name: len(result)
        for name, result in observed.items()
        if result
    }
    target = gate.stem

    if args.expectation == "pass":
        if firing:
            print(
                json.dumps(
                    {
                        "refusal": "REFUSED_GATE_ROWS_ON_PASS",
                        "gates": firing,
                    }
                ),
                file=sys.stderr,
            )
            return 2
        print(
            json.dumps(
                {
                    "observed": "pass",
                    "gates_run": [candidate.stem for candidate in gates],
                    "rows": 0,
                },
                sort_keys=True,
            )
        )
        return 0

    if target not in firing:
        print(
            json.dumps(
                {
                    "refusal": "REFUSED_EXPECTED_GATE_DID_NOT_FIRE",
                    "gate": target,
                    "firing": firing,
                }
            ),
            file=sys.stderr,
        )
        return 2

    other = {name: count for name, count in firing.items() if name != target}
    if other:
        print(
            json.dumps(
                {
                    "refusal": "REFUSED_MORE_THAN_ONE_GATE_FIRED",
                    "target": target,
                    "others": other,
                }
            ),
            file=sys.stderr,
        )
        return 2

    print(
        json.dumps(
            {
                "observed": "fail",
                "gate": target,
                "rows": firing[target],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
