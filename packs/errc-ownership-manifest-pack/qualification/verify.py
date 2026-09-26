#!/usr/bin/env python3
"""Anti-vacuity court for ERRC ownership claims."""
from __future__ import annotations

from pathlib import Path
import sys

try:
    from rdflib import Graph
except ImportError as exc:
    raise SystemExit("REFUSED:VERIFIER_UNAVAILABLE:rdflib") from exc

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GATES = ROOT / "gates"

EXPECTED = {
    "negative-exact-subject.ttl": "010_exact_subject.rq",
    "negative-generated.ttl": "020_generated_requires_generator.rq",
    "negative-reused.ttl": "030_reused_requires_source.rq",
    "negative-materialized.ttl": "040_materialized_requires_receipt.rq",
    "negative-ownership.ttl": "050_known_ownership_only.rq",
    "negative-duplicate.ttl": "060_unique_path_per_subject.rq",
}

def rows(fixture: Path) -> dict[str, int]:
    graph = Graph()
    graph.parse(ROOT / "ontology.ttl", format="turtle")
    graph.parse(fixture, format="turtle")
    return {
        gate.name: len(list(graph.query(gate.read_text(encoding="utf-8"))))
        for gate in sorted(GATES.glob("*.rq"))
    }

def main() -> int:
    clean = rows(FIXTURES / "positive.ttl")
    if any(clean.values()):
        print(f"REFUSED:POSITIVE_OWNERSHIP_FIXTURE:{clean}")
        return 1

    failures: list[str] = []
    for fixture_name, expected_gate in EXPECTED.items():
        observed = rows(FIXTURES / fixture_name)
        if observed.get(expected_gate, 0) < 1:
            failures.append(f"{fixture_name}:{expected_gate}:{observed}")

    if failures:
        print("REFUSED:OWNERSHIP_ANTI_VACUITY:" + "|".join(failures))
        return 1

    print("ADMITTED:errc ownership manifest court")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
