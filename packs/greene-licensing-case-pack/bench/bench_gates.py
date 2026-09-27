#!/usr/bin/env python3
"""Deterministic timing benchmark for greene-licensing-case-pack's gates.

Real collaborators only: the pack's real Turtle files (plus the import union
ggen evaluates), the real gates/*.rq evaluated by rdflib, the real
runners/semantic_runner.py as a subprocess, and adversarial literals shaped
to trigger catastrophic regex backtracking. Prints one JSON object; with
--out it also writes it. The committed receipt (bench/receipt-v26.9.26.json)
is the regression baseline tests/test_greene_licensing_case_hardening.py
bounds against.

    python3 packs/greene-licensing-case-pack/bench/bench_gates.py [--repeats 5] [--out FILE]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

from rdflib import Graph, Literal, URIRef

PACK = Path(__file__).resolve().parents[1]
PACKS = PACK.parent
GATES = sorted((PACK / "gates").glob("*.rq"))
BODY = URIRef("https://ggen.dev/ontology/greene-licensing-case#body")
S4 = URIRef("https://ggen.dev/ontology/greene-licensing-case#s4")
ADVERSARIAL_LENGTH = 20000
# A later run regresses when a p50 exceeds max(recorded * factor, floor). The
# factor absorbs host load (measured spread up to ~2x on a shared laptop); a
# catastrophic-backtracking regression is >10x, so it still trips the bound.
REGRESSION_BOUND = {"factor": 4, "floor_seconds": 5.0}
ADVERSARIAL = {
    "unterminated-double-quote": '"a' + " a" * (ADVERSARIAL_LENGTH // 2),
    "unterminated-single-quote": " 'a" + " a" * (ADVERSARIAL_LENGTH // 2),
    "ampersand-run": "&a" * (ADVERSARIAL_LENGTH // 2),
    "soft-wrap-run": "-\n" * (ADVERSARIAL_LENGTH // 2),
    "angle-run": "<" * ADVERSARIAL_LENGTH,
    "stem-prefix-run": "endor " * (ADVERSARIAL_LENGTH // 6),
}


def union_graph() -> Graph:
    graph = Graph()
    for path in (PACK / "ontology.ttl", PACK / "ontology" / "greene-case.ttl", PACK / "ontology" / "greene-deck.ttl",
                 PACK / "ontology" / "cs-pres-bridge.ttl", PACKS / "semantic-case-study-pack" / "ontology.ttl",
                 PACKS / "pptx-presentation-pack" / "ontology.ttl", PACKS / "evidence-standing-pack" / "ontology.ttl",
                 PACKS / "decision-optionality-pack" / "ontology.ttl"):
        graph.parse(path, format="turtle")
    return graph


def timed_rows(graph: Graph, gate: Path) -> tuple[float, int]:
    query = gate.read_text(encoding="utf-8")
    start = time.perf_counter()
    count = len(list(graph.query(query)))
    return time.perf_counter() - start, count


def measure(repeats: int, subject: str | None = None) -> dict:
    graph = union_graph()
    gates = {}
    for gate in GATES:
        samples, counts = zip(*(timed_rows(graph, gate) for _ in range(repeats)))
        gates[gate.stem] = {"p50_seconds": round(statistics.median(samples), 4),
                            "max_seconds": round(max(samples), 4), "rows": sorted(set(counts))}
    adversarial = {}
    for name, literal in ADVERSARIAL.items():
        mutated = union_graph()
        mutated.add((S4, BODY, Literal(literal)))
        per_gate = {gate.stem: timed_rows(mutated, gate) for gate in GATES}
        adversarial[name] = {"total_seconds": round(sum(s for s, _ in per_gate.values()), 4),
                             "rows": {stem: rows for stem, (_, rows) in per_gate.items()}}
    runner = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = subprocess.run([sys.executable, "runners/semantic_runner.py", "--gate", str(GATES[0]),
                                 "--witness", str(PACK / "witnesses" / "pass" / f"{GATES[0].stem}.ttl"),
                                 "--expectation", "pass"], cwd=PACK, capture_output=True, text=True)
        runner.append(time.perf_counter() - start)
        if result.returncode != 0:
            raise SystemExit(f"runner failed: {result.stderr}")
    return {
        "schema": "ggen-marketplace.bench/greene-licensing-case-gates/1",
        "gate_digests": {g.stem: hashlib.sha256(g.read_bytes()).hexdigest() for g in GATES},
        "graph_triples": len(graph),
        "repeats": repeats,
        "adversarial_literal_length": ADVERSARIAL_LENGTH,
        "gates": gates,
        "adversarial": adversarial,
        "runner_pass_witness": {"p50_seconds": round(statistics.median(runner), 4),
                                "max_seconds": round(max(runner), 4)},
        "regression_bound": REGRESSION_BOUND,
        "subject": subject,
        "host": {"python": platform.python_version(), "machine": platform.machine(), "system": platform.system()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--subject", help="exact repository@sha the measured gate bytes were materialized from")
    args = parser.parse_args()
    report = measure(args.repeats, args.subject)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
