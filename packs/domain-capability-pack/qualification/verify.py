#!/usr/bin/env python3
"""Deterministic violation-row anti-vacuity court for this pack's gates.

Composed from the exemplar pattern (packs/qualified-capability-ecology-pack/
qualification/verify.py): every gate must be CLEAN on the positive fixture and
every new gate must be FIRED by its named negative fixture. A gate with no
witnessed refusal carries no bits; this runner is the witnessed firing.

Run: python3 packs/domain-capability-pack/qualification/verify.py   (exit 0 = admit)
"""
from __future__ import annotations

from pathlib import Path

try:
    from rdflib import Graph
except ImportError as exc:  # pragma: no cover
    raise SystemExit("REFUSED:VERIFIER_UNAVAILABLE:rdflib") from exc

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "gates"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

# Every contract-layer gate (040-090) needs >=1 negative fixture that FIRES it.
# The transcription gates (010/020/030) are exercised by the pack's real worked
# instance in ontology.ttl (drift guard) and by the marketplace's global court.
NEGATIVE_EXPECTATIONS = {
    "negative-missing-required-contract-fields.ttl": {"040_required_contract_fields.rq"},
    "negative-capability-without-realization.ttl": {"050_capability_requires_realization.rq"},
    "negative-realization-without-qualification.ttl": {"060_realization_requires_qualification.rq"},
    "negative-available-without-authority.ttl": {"070_availability_requires_authority.rq"},
    "negative-do-authority.ttl": {"080_no_do_authority.rq"},
    "negative-runtime-unfrozen.ttl": {"090_runtime_only_frozen.rq"},
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

    print("ADMITTED:dcp semantic court (9 gates clean on positive; 6 negative fixtures witnessed firing)")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
