#!/usr/bin/env python3
"""Deterministic violation-row anti-vacuity court for network-capability-pack.

Every gate in gates/ is a violation-row SELECT evaluated over the union of
ontology.ttl and one fixture. The positive fixture must yield zero rows under
every gate; each negative fixture must fire at least its named gate (the exact
single-gate property is asserted by tests/test_network_capability_pack.py).
Exit 0 = ADMITTED, nonzero = REFUSED. Stdlib + rdflib only; no network, no
subprocess, no actuation.
"""
from __future__ import annotations

from pathlib import Path
import sys

try:
    from rdflib import Graph
except ImportError as exc:  # pragma: no cover
    raise SystemExit("REFUSED:VERIFIER_UNAVAILABLE:rdflib") from exc

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "gates"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

NEGATIVE_EXPECTATIONS = {
    "negative-010_capability_requires_realization.ttl": {
        "010_capability_requires_realization.rq",
    },
    "negative-020_realization_requires_qualification_conditions.ttl": {
        "020_realization_requires_qualification_conditions.rq",
    },
    "negative-030_capability_requires_typed_failure_set.ttl": {
        "030_capability_requires_typed_failure_set.rq",
    },
    "negative-040_consequential_requires_authority.ttl": {
        "040_consequential_requires_authority.rq",
    },
    "negative-050_endpoint_resolution_precondition_required.ttl": {
        "050_endpoint_resolution_precondition_required.rq",
    },
    "negative-060_retry_semantics_declared.ttl": {
        "060_retry_semantics_declared.rq",
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

    # The ontology's own eight capabilities are the primary positive instance:
    # they must be clean under every gate with no fixture at all (this is
    # exactly what the real-ggen qualification pass evaluates).
    ontology_graph = Graph()
    ontology_graph.parse(ROOT / "ontology.ttl", format="turtle")
    ontology_clean = {
        gate.name: len(list(ontology_graph.query(gate.read_text(encoding="utf-8"))))
        for gate in sorted(GATES.glob("*.rq"))
    }
    if any(ontology_clean.values()):
        print(f"REFUSED:ONTOLOGY_INSTANCE:{ontology_clean}")
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

    print("ADMITTED:network-capability semantic court")
    return 0


if __name__ == "__main__":
    sys.exit(main())
