#!/usr/bin/env python3
"""Deterministic violation-row witness runner for a2a-capability-pack gates.

Court contract (gate-court.toml, case_key = exact-stem):

* witnesses/pass/<stem>.ttl  -- graph = ontology.ttl + witness; EVERY gate
  must return zero rows.
* witnesses/fail/<stem>.ttl  -- graph = ontology.ttl + witness; the gate with
  the exact matching stem must return at least one row (anti-vacuity: a gate
  whose firing fixture never fires carries no bits).

inspection != execution: this runner proves graph-level gate behavior only.
It never claims execution standing for any modeled capability.
"""
from __future__ import annotations

from pathlib import Path
import sys

try:
    from rdflib import Graph
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("REFUSED:VERIFIER_UNAVAILABLE:rdflib") from exc

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "gates"
PASS = ROOT / "witnesses" / "pass"
FAIL = ROOT / "witnesses" / "fail"


def evaluate(graph_path: Path) -> dict[str, int]:
    graph = Graph()
    graph.parse(ROOT / "ontology.ttl", format="turtle")
    graph.parse(graph_path, format="turtle")
    return {
        gate.name: len(list(graph.query(gate.read_text(encoding="utf-8"))))
        for gate in sorted(GATES.glob("*.rq"))
    }


def main() -> int:
    gate_names = sorted(path.stem for path in GATES.glob("*.rq"))
    if not gate_names:
        print("REFUSED:NO_GATES")
        return 1

    failures: list[str] = []

    for witness in sorted(PASS.glob("*.ttl")):
        result = evaluate(witness)
        fired = {gate for gate, count in result.items() if count}
        if fired:
            failures.append(f"pass/{witness.name}:fired={sorted(fired)}:result={result}")

    for witness in sorted(FAIL.glob("*.ttl")):
        target = witness.stem
        if target not in gate_names:
            failures.append(f"fail/{witness.name}:no_matching_gate:{target}")
            continue
        result = evaluate(witness)
        if result.get(f"{target}.rq", 0) < 1:
            failures.append(f"fail/{witness.name}:target_did_not_fire:{target}:result={result}")

    pass_stems = {path.stem for path in PASS.glob("*.ttl")}
    fail_stems = {path.stem for path in FAIL.glob("*.ttl")}
    missing_pass = sorted(set(gate_names) - pass_stems)
    missing_fail = sorted(set(gate_names) - fail_stems)
    if missing_pass or missing_fail:
        failures.append(f"case_correspondence:missing_pass={missing_pass}:missing_fail={missing_fail}")

    if failures:
        print("REFUSED:WITNESS_COURT:" + "|".join(failures))
        return 1

    print(f"ADMITTED:a2a-capability-pack witness court ({len(gate_names)} gates, "
          f"{len(pass_stems)} pass + {len(fail_stems)} fail witnesses)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
