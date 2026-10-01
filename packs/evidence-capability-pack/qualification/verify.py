#!/usr/bin/env python3
"""Deterministic violation-row qualification runner for ecap gates.

Positive contract: gates/*.rq return ZERO rows over ontology.ttl +
qualification/fixtures/positive.ttl. Anti-vacuity contract: each
qualification/fixtures/negative-*.ttl makes its named gate return at least one
row (a gate with no witnessed refusal carries no bits).
"""
from __future__ import annotations

from pathlib import Path
import sys

try:
    from rdflib import Graph
except ImportError as exc:
    raise SystemExit("REFUSED:VERIFIER_UNAVAILABLE:rdflib") from exc

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "gates"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

NEGATIVE_EXPECTATIONS = {
    "negative-pinned-impostor.ttl": {"010_pinned_capability_identity.rq"},
    "negative-incomplete-capability.ttl": {"020_capability_contract_complete.rq"},
    "negative-capability-without-realization.ttl": {"030_capability_without_realization.rq"},
    "negative-realization-without-qualification.ttl": {"040_realization_without_qualification.rq"},
    "negative-receipt-missing-field.ttl": {"050_receipt_missing_field.rq"},
    "negative-evidence-unbound.ttl": {"060_evidence_unbound_to_subject.rq"},
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
    clean = evaluate(FIXTURES / "positive.ttl")
    if any(clean.values()):
        print(f"REFUSED:POSITIVE_FIXTURE:{clean}")
        return 1

    failures: list[str] = []
    for fixture_name, expected in NEGATIVE_EXPECTATIONS.items():
        result = evaluate(FIXTURES / fixture_name)
        fired = {gate for gate, count in result.items() if count}
        missing = sorted(expected - fired)
        if missing:
            failures.append(f"{fixture_name}:missing={missing}:result={result}")

    if failures:
        print("REFUSED:NEGATIVE_ANTI_VACUITY:" + "|".join(failures))
        return 1

    print("ADMITTED:ecap semantic court")
    return 0


if __name__ == "__main__":
    sys.exit(main())
