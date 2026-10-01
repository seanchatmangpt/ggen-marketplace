#!/usr/bin/env python3
"""Deterministic anti-vacuity court for durability-capability-pack gates.

Contract (mirrors packs/qualified-capability-ecology-pack/qualification/verify.py):

  1. ontology.ttl ALONE must be gate-clean (the admitted pack graph carries no
     violation rows) -- the real-ggen qualification surface.
  2. ontology.ttl + fixtures/positive.ttl must be gate-clean (the conforming
     runtime claim world: all lawful resume outcomes modeled).
  3. Each negative fixture below must be refused by EXACTLY its declared gates --
     no fewer (vacuous gate) and no more (over-firing court).

Exit 0 = court admits; nonzero = REFUSED with the failing matrix on stdout/stderr.
The last stdout line is a JSON payload with standing/case_count for test wiring.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from rdflib import Graph
except ImportError as exc:  # pragma: no cover
    raise SystemExit("REFUSED:VERIFIER_UNAVAILABLE:rdflib") from exc

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "gates"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

# fixture -> the exact set of gates it must fire (no more, no fewer)
NEGATIVE_EXPECTATIONS: dict[str, set[str]] = {
    "negative-capability-without-realization.ttl": {"020_capability_without_realization.rq"},
    "negative-checkpoint-without-subject-digest.ttl": {"030_checkpoint_without_subject_digest.rq"},
    "negative-replay-without-determinism-evidence.ttl": {"040_replay_without_determinism_evidence.rq"},
    "negative-resume-version-boundary.ttl": {"050_resume_across_version_without_requalification.rq"},
    "negative-authority-gap.ttl": {"060_authority_gap_unmodeled_on_halt.rq"},
    "negative-realization-without-qualification.ttl": {"070_realization_without_qualification_conditions.rq"},
    "negative-missing-required-fields.ttl": {
        "010_required.rq",
        "020_capability_without_realization.rq",
    },
    "negative-resume-outcome-enum.ttl": {"010_required.rq"},
}


def load_graph(fixture_path: Path | None) -> Graph:
    graph = Graph()
    graph.parse(ROOT / "ontology.ttl", format="turtle")
    if fixture_path is not None:
        graph.parse(fixture_path, format="turtle")
    return graph


def gates() -> list[Path]:
    return sorted(GATES.glob("*.rq"))


def refusing_gates(graph: Graph) -> dict[str, int]:
    result: dict[str, int] = {}
    for gate in gates():
        count = len(list(graph.query(gate.read_text(encoding="utf-8"))))
        if count:
            result[gate.name] = count
    return result


def evaluate(graph_path: Path) -> dict[str, int]:
    return {
        gate.name: len(list(load_graph(graph_path).query(gate.read_text(encoding="utf-8"))))
        for gate in gates()
    }


def main() -> int:
    failures: list[str] = []

    # 1 + 2: the admitted graph and the conforming claim world must be clean.
    for label, fixture in (("pack-graph", None), ("positive", FIXTURES / "positive.ttl")):
        rows = evaluate(fixture) if fixture else refusing_gates(load_graph(None))
        fired = {name: count for name, count in rows.items() if count}
        if fired:
            failures.append(f"{label}:expected-clean:fired={fired}")

    # 3: every negative fixture fires EXACTLY its declared gate set.
    for fixture_name, expected in NEGATIVE_EXPECTATIONS.items():
        path = FIXTURES / fixture_name
        if not path.is_file():
            failures.append(f"{fixture_name}:missing-fixture")
            continue
        fired = set(refusing_gates(load_graph(path)))
        missing = sorted(expected - fired)
        extra = sorted(fired - expected)
        if missing:
            failures.append(f"{fixture_name}:vacuous:missing={missing}")
        if extra:
            failures.append(f"{fixture_name}:over-firing:extra={extra}")

    case_count = len(gates()) + len(NEGATIVE_EXPECTATIONS)
    payload = {
        "standing": "REFUSED" if failures else "ALIVE",
        "case_count": case_count,
        "gate_count": len(gates()),
        "negative_fixture_count": len(NEGATIVE_EXPECTATIONS),
        "failures": failures,
        "schema": "ggen.marketplace.durability-capability-court/1",
    }
    print(json.dumps(payload, sort_keys=True))
    if failures:
        for failure in failures:
            print(f"REFUSED:DURABILITY_COURT:{failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
