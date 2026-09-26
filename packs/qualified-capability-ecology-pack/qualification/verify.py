#!/usr/bin/env python3
"""Deterministic violation-row qualification runner for QCE gates."""
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
    "negative-mutable-subject.ttl": {"010_candidate_requires_immutable_subject.rq"},
    "negative-unqualified-freeze.ttl": {"020_freeze_requires_qualification.rq"},
    "negative-runtime-candidate.ttl": {"030_runtime_only_frozen.rq"},
    "negative-actuating-evolution.ttl": {"040_evolution_is_non_actuating.rq"},
    "negative-substitution.ttl": {"050_substitution_requires_consequence_preservation.rq"},
    "negative-retirement.ttl": {"060_retirement_requires_negative_human_work_delta.rq"},
    "negative-authority-increase.ttl": {"070_no_authority_increase.rq"},
    "negative-no-replay.ttl": {"080_replay_required.rq"},
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

    print("ADMITTED:qce semantic court")
    return 0

if __name__ == "__main__":
    sys.exit(main())
