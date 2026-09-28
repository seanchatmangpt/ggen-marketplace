#!/usr/bin/env python3
"""Execute governance-gate conformance vectors against the generated contract template."""

from __future__ import annotations

import importlib.util
import json
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

PACK = Path(__file__).parents[2]
CONTRACT = PACK / "templates" / "governance_gate_contract.py.tera"
VECTORS = PACK / "vectors" / "conformance.json"


def load_contract():
    name = "governance_gate_vector_contract"
    loader = SourceFileLoader(name, str(CONTRACT))
    spec = importlib.util.spec_from_loader(name, loader)
    if spec is None:
        raise RuntimeError("CONTRACT_LOADER_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


def main() -> int:
    contract = load_contract()
    payload = json.loads(VECTORS.read_text(encoding="utf-8"))
    results = []

    for vector in payload["cases"]:
        decision = contract.classify(contract.GateInput(**vector["input"]))
        actual = {
            "standing": decision.standing.value,
            "ready_for_do": decision.ready_for_do,
            "refusal_code": decision.refusal_code,
        }
        qualified = actual == vector["expected"]
        receipt = contract.decision_receipt(vector["id"], contract.GateInput(**vector["input"]))
        replayed = contract.replay_receipt(receipt)
        results.append(
            {
                "id": vector["id"],
                "qualified": qualified,
                "expected": vector["expected"],
                "actual": actual,
                "receipt_digest": receipt.digest,
                "replay_equal": replayed == receipt.decision,
            }
        )

    standing = (
        "ALIVE"
        if results
        and all(row["qualified"] and row["replay_equal"] for row in results)
        else "REFUSED"
    )
    print(
        json.dumps(
            {
                "schema": "ggen.governance-gate-vector-receipt/1",
                "standing": standing,
                "vector_count": len(results),
                "results": results,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if standing == "ALIVE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
