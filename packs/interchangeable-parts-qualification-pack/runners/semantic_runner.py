#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rdflib import Graph
from pyshacl import validate as shacl_validate

PACK_ROOT = Path(__file__).resolve().parents[1]
GATES_DIR = PACK_ROOT / "gates"
SHAPES = PACK_ROOT / "ontology" / "shapes.ttl"
ONTOLOGY = PACK_ROOT / "ontology.ttl"


def load_graph(path: Path) -> Graph:
    graph = Graph()
    graph.parse(path, format="turtle")
    return graph


def gate_rows(gate_path: Path, data: Graph) -> list:
    return list(data.query(gate_path.read_text(encoding="utf-8")))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--witness", type=Path, required=True)
    parser.add_argument("--expectation", choices=("pass", "fail"), required=True)
    args = parser.parse_args()

    try:
        witness_path = args.witness.resolve()
        gate_path = args.gate.resolve()
        if not witness_path.is_file() or not gate_path.is_file():
            raise FileNotFoundError("gate or witness missing")
        data = load_graph(witness_path)
        gates = sorted(GATES_DIR.glob("*.rq"))
        if not gates:
            raise FileNotFoundError("no semantic gates")
    except (OSError, FileNotFoundError) as error:
        print(json.dumps({"refusal": "REFUSED_STRUCTURAL", "error": str(error)}), file=sys.stderr)
        return 3

    if args.expectation == "pass":
        conforms, _, _ = shacl_validate(
            data_graph=data,
            shacl_graph=str(SHAPES),
            ont_graph=str(ONTOLOGY),
            inference="none",
            advanced=True,
        )
        if not conforms:
            print(json.dumps({"refusal": "REFUSED_SHACL"}), file=sys.stderr)
            return 2
        offending = {candidate.stem: len(rows) for candidate in gates if (rows := gate_rows(candidate, data))}
        if offending:
            print(json.dumps({"refusal": "REFUSED_GATE_ROWS_ON_PASS", "gates": offending}), file=sys.stderr)
            return 2
        print(json.dumps({"observed": "pass", "gates_run": [g.stem for g in gates], "rows": 0}))
        return 0

    target = gate_path.stem
    target_rows = []
    other_rows = {}
    for candidate in gates:
        rows = gate_rows(candidate, data)
        if candidate.stem == target:
            target_rows = rows
        elif rows:
            other_rows[candidate.stem] = len(rows)

    if not target_rows:
        print(json.dumps({"refusal": "REFUSED_EXPECTED_GATE_DID_NOT_FIRE", "gate": target}), file=sys.stderr)
        return 2
    if other_rows:
        print(json.dumps({"refusal": "REFUSED_MORE_THAN_ONE_GATE_FIRED", "others": other_rows}), file=sys.stderr)
        return 2
    print(json.dumps({"observed": "fail", "gate": target, "rows": len(target_rows)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
