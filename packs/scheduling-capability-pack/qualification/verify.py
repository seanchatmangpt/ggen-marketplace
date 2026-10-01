#!/usr/bin/env python3
"""Anti-vacuity court runner for scheduling-capability-pack gates.

Semantics (mirrors qualified-capability-ecology-pack, tightened):
- gates on ontology.ttl + qualification/fixtures/positive.ttl must return
  ZERO rows (the lawful world passes);
- each negative fixture must fire EXACTLY its named gates — no more, no
  fewer — so every gate is proven both able to fire (non-vacuous) and
  discriminating (each negative violates exactly one invariant).

Real execution throughout: Turtle + SPARQL via rdflib. Rows are observed
query results, never asserted shapes.
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

# negative fixture -> exact set of gates it must fire (by file name).
NEGATIVE_EXPECTATIONS = {
    "negative-capability-without-realization.ttl": {
        "010_capability_requires_realization.rq",
    },
    "negative-realization-without-qualification.ttl": {
        "020_realization_requires_qualification.rq",
    },
    "negative-missed-fire-policy-missing.ttl": {
        "030_missed_fire_policy_required.rq",
    },
    "negative-authority-unbound.ttl": {
        "040_consequential_requires_authority.rq",
    },
    "negative-provider-token-identity.ttl": {
        "050_capability_identity_impl_free.rq",
    },
    "negative-recurring-without-timezone.ttl": {
        "060_recurring_requires_timezone_anchoring.rq",
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
    clean = evaluate(FIXTURES / "positive.ttl")
    if any(clean.values()):
        print(f"REFUSED:POSITIVE_FIXTURE:{clean}")
        return 1

    failures: list[str] = []
    for fixture_name, expected in NEGATIVE_EXPECTATIONS.items():
        result = evaluate(FIXTURES / fixture_name)
        fired = {gate for gate, count in result.items() if count}
        missing = sorted(expected - fired)
        unexpected = sorted(fired - expected)
        if missing or unexpected:
            failures.append(
                f"{fixture_name}:missing={missing}:unexpected={unexpected}:result={result}"
            )

    if failures:
        print("REFUSED:NEGATIVE_ANTI_VACUITY:" + "|".join(failures))
        return 1

    print("ADMITTED:scheduling-capability-pack semantic court")
    return 0


if __name__ == "__main__":
    sys.exit(main())
