#!/usr/bin/env python3
"""Semantic runner for the semantic-gate-witness-court contract.

Adapted from packs/industry-manufacturing-dflss/runners/semantic_runner.py (the
dflss-exemplar runner): same contract, same exit codes, same refusal vocabulary,
same exactly-one-law fail semantics. Only differences, both documented:
  1. This pack has no ontology/shapes.ttl SHACL twin, so the dflss runner's
     SHACL-conformance leg over pass witnesses is not carried here; the pass
     witness contract is zero rows from every gate (qualification/verify.py
     additionally proves the pack graph itself clean).
  2. Gates, witnesses and ontology resolve relative to this pack root, so this
     runner judges industry-pharma-21cfr witnesses against
     industry-pharma-21cfr gates only.

Contract (argv tokens {gate} {witness} {expectation} are formatted by the
court):

    semantic_runner.py --gate <gate.rq> --witness <witness.ttl> \
        --expectation pass|fail

Semantics:
  pass  -- witness graph must return zero rows from every gate in gates/.
  fail  -- witness must return >= 1 row from EXACTLY the gate named by
           --gate (stem match) and zero rows from every other gate.

Exit codes: 0 expectation observed; 2 expectation violated (REFUSED);
3 structural error (missing file, unparseable graph, or a --gate that is
not one of this pack's gates -- a gate outside gates/ sharing a stem must
not be judged as if it were the pack's own).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rdflib import Graph

PACK_ROOT = Path(__file__).resolve().parents[1]
GATES_DIR = PACK_ROOT / "gates"
ONTOLOGY = PACK_ROOT / "ontology.ttl"


def load_graph(path: Path) -> Graph:
    graph = Graph()
    graph.parse(path, format="turtle")
    return graph


def gate_rows(gate_path: Path, data: Graph) -> list:
    return list(data.query(gate_path.read_text(encoding="utf-8")))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--witness", type=Path, required=True)
    parser.add_argument("--expectation", choices=("pass", "fail"), required=True)
    args = parser.parse_args()

    try:
        witness_path = args.witness.resolve()
        gate_path = args.gate.resolve()
        if not witness_path.is_file():
            raise FileNotFoundError(f"witness not found: {args.witness}")
        if not gate_path.is_file():
            raise FileNotFoundError(f"gate not found: {args.gate}")
        gates = sorted(GATES_DIR.glob("*.rq"))
        if not gates:
            raise FileNotFoundError(f"no gates in {GATES_DIR}")
        if gate_path not in {candidate.resolve() for candidate in gates}:
            raise FileNotFoundError(f"gate is not one of this pack's gates: {args.gate}")
        data = load_graph(witness_path)
    except OSError as error:
        print(json.dumps({"refusal": "REFUSED_STRUCTURAL", "error": str(error)}), file=sys.stderr)
        return 3
    except Exception as error:  # rdflib raises parser-specific types for malformed Turtle
        print(json.dumps({"refusal": "REFUSED_STRUCTURAL", "error": f"unparseable witness: {type(error).__name__}"}),
              file=sys.stderr)
        return 3

    offending = {}
    target_stem = gate_path.stem
    target_rows: list = []
    for candidate in gates:
        rows = gate_rows(candidate, data)
        if candidate.stem == target_stem:
            target_rows = rows
        elif rows:
            offending[candidate.stem] = [tuple(str(term) for term in row) for row in rows]

    if args.expectation == "pass":
        if offending or target_rows:
            all_rows = dict(offending)
            if target_rows:
                all_rows[target_stem] = [tuple(str(term) for term in row) for row in target_rows]
            print(json.dumps({"refusal": "REFUSED_GATE_ROWS_ON_PASS", "gates": all_rows}), file=sys.stderr)
            return 2
        print(json.dumps({"observed": "pass", "witness": witness_path.name,
                          "gates_run": [g.stem for g in gates], "rows": 0}))
        return 0

    # expectation == fail: exactly the named gate fires, no other gate does.
    if not target_rows:
        print(json.dumps({"refusal": "REFUSED_EXPECTED_GATE_DID_NOT_FIRE",
                          "gate": target_stem, "witness": witness_path.name}), file=sys.stderr)
        return 2
    if offending:
        print(json.dumps({"refusal": "REFUSED_MORE_THAN_ONE_GATE_FIRED",
                          "gate": target_stem, "others": offending}), file=sys.stderr)
        return 2
    print(json.dumps({"observed": "fail", "witness": witness_path.name, "gate": target_stem,
                      "rows": len(target_rows)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
