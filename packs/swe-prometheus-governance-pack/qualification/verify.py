#!/usr/bin/env python3
"""Deterministic violation-row court for the SWE-Prometheus governance pack."""
from __future__ import annotations

from pathlib import Path
import json
import sys

try:
    from rdflib import Graph
except ImportError as exc:
    raise SystemExit("REFUSED:VERIFIER_UNAVAILABLE:rdflib") from exc

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "gates"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

EXPECTED_ROWS = {
    "neg_all.ttl": {
        "010_exact_identity.rq": 2,
        "020_dimension_universe.rq": 6,
        "030_detected_requires_mutation_receipt.rq": 1,
        "040_paired_score_shape.rq": 3,
    },
    "neg_enums.ttl": {
        "050_closed_enums.rq": 9,
    },
    "neg_receipts.ttl": {
        "060_receipt_binding.rq": 6,
    },
    "neg_scores.ttl": {
        "070_score_cardinality.rq": 6,
    },
    "neg_plans.ttl": {
        "080_plan_shape.rq": 13,
    },
    "neg_mutation_payload.ttl": {
        "090_mutation_payload.rq": 7,
    },
    "neg_command_boundary.ttl": {
        "100_command_boundary.rq": 6,
    },
}


def evaluate(graph_path: Path) -> dict[str, int]:
    graph = Graph()
    graph.parse(ROOT / "ontology.ttl", format="turtle")
    graph.parse(graph_path, format="turtle")
    return {
        gate.name: len(list(graph.query(gate.read_text(encoding="utf-8"))))
        for gate in sorted(GATES.glob("*.rq"))
    }


def main() -> int:
    clean = evaluate(FIXTURES / "pos_clean.ttl")
    if any(clean.values()):
        print(
            "REFUSED:POSITIVE_FIXTURE:"
            + json.dumps(clean, sort_keys=True, separators=(",", ":"))
        )
        return 1

    failures: list[str] = []
    observations: dict[str, dict[str, int]] = {
        "pos_clean.ttl": clean,
    }
    for fixture_name, expected in EXPECTED_ROWS.items():
        result = evaluate(FIXTURES / fixture_name)
        observations[fixture_name] = result
        for gate, expected_rows in expected.items():
            actual = result.get(gate, 0)
            if actual != expected_rows:
                failures.append(
                    f"{fixture_name}:{gate}:expected={expected_rows}:actual={actual}"
                )
    if failures:
        print("REFUSED:SEMANTIC_GATE_COURT:" + "|".join(failures))
        return 1

    print(
        "ADMITTED:swe-prometheus-governance semantic court:"
        + json.dumps(observations, sort_keys=True, separators=(",", ":"))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
