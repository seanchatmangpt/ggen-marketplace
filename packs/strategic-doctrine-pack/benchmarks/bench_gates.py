#!/usr/bin/env python3
"""Deterministic latency benchmark for the six strategic-doctrine gates.

Measures wall time of every gate in gates/ (real rdflib SPARQL engine, real
query text) over:
  - the shipped doctrine graph (ontology + world model + 33-entry catalog +
    entrant-world fixture), and
  - synthetic doctrine graphs of N operationalized strategies (4 ordered
    steps, one falsifier, one condition, one objective each), built from own
    synthetic text only, used to bound growth as the catalog scales.

Usage:
    python3 benchmarks/bench_gates.py --write     # re-record benchmarks/receipt.json
    python3 benchmarks/bench_gates.py             # print a fresh measurement

The receipt carries a regression bound consumed by
tests/test_strategic_doctrine_pack_hardening.py: each gate's observed median
must stay within max(recorded * factor, floor_seconds), the synthetic
64-strategy total within scale_4x_factor of the 16-strategy total, and each
gate's own 64/16 ratio within per_gate_scale_4x_factor (so one superlinear
gate cannot hide behind fast ones in the total).
Authority NONE: the benchmark reads graphs and writes only its own receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import statistics
import sys
import time
from pathlib import Path

import rdflib
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD

PACK = Path(__file__).resolve().parents[1]
GATES = sorted((PACK / "gates").glob("*.rq"))
RECEIPT = PACK / "benchmarks" / "receipt.json"
SD = Namespace("https://ggen.dev/ontology/strategic-doctrine#")
ORG = Namespace("http://www.w3.org/ns/org#")
DOCTRINE_FILES = ("ontology.ttl", "ontology/world-model.ttl", "ontology/doctrine-33.ttl",
                  "fixtures/entrant-world.ttl")
OPERATORS = ("shape", "probe", "conceal", "reveal", "concentrate", "disperse", "delay",
             "accelerate", "commit", "withdraw", "divide", "combine", "substitute", "transform")
# factor/floor_seconds bound each doctrine gate against its recorded median.
# scale_4x_factor bounds the synthetic 64/16 total. per_gate_scale_4x_factor
# bounds EACH gate's own 64/16 ratio (the 64-strategy graph has 3x the
# triples, so a linear gate sits near 3x and a quadratic one near 9x);
# gates whose 64-strategy median is under per_gate_scale_floor_seconds are
# below timer noise and exempt from the per-gate ratio.
REGRESSION_BOUND = {"factor": 5.0, "floor_seconds": 0.5, "scale_4x_factor": 6.0,
                    "per_gate_scale_4x_factor": 4.5, "per_gate_scale_floor_seconds": 0.5}


def per_gate_scale_violations(small: dict, large: dict, bound: dict = REGRESSION_BOUND) -> dict[str, float]:
    """Gates whose 64-strategy median grew past the per-gate 4x bound."""
    out: dict[str, float] = {}
    for stem, large_seconds in large["median_seconds"].items():
        if large_seconds < bound["per_gate_scale_floor_seconds"]:
            continue
        small_seconds = max(small["median_seconds"][stem], 1e-6)
        ratio = large_seconds / small_seconds
        if ratio > bound["per_gate_scale_4x_factor"]:
            out[stem] = round(ratio, 2)
    return out


def doctrine_graph() -> Graph:
    graph = Graph()
    for item in DOCTRINE_FILES:
        graph.parse(PACK / item, format="turtle")
    return graph


def synthetic_graph(strategies: int) -> Graph:
    """Pack ontology plus N synthetic operationalized strategies (own text)."""
    graph = Graph()
    graph.parse(PACK / "ontology.ttl", format="turtle")
    base = "urn:example:bench:"
    for index in range(1, strategies + 1):
        strategy = URIRef(f"{base}strategy-{index}")
        graph.add((strategy, RDF.type, SD.Strategy))
        graph.add((strategy, SD.ordinal, Literal(index)))
        graph.add((strategy, SD.shortTitle, Literal(f"Synthetic bench entry {index}")))
        for order in range(1, 5):
            step = URIRef(f"{base}strategy-{index}-step-{order}")
            graph.add((strategy, SD.composedOf, step))
            graph.add((step, RDF.type, SD.Step))
            graph.add((step, SD.order, Literal(order, datatype=XSD.integer)))
            graph.add((step, SD.operator, SD[OPERATORS[(index + order) % len(OPERATORS)]]))
        falsifier = URIRef(f"{base}falsifier-{index}")
        graph.add((strategy, SD.hasFalsifier, falsifier))
        graph.add((falsifier, RDF.type, SD.Falsifier))
        graph.add((falsifier, SD.refutedWhen, Literal(f"bench metric {index} stays flat for 90 days")))
        condition = URIRef(f"{base}condition-{index}")
        graph.add((strategy, SD.appliesWhen, condition))
        graph.add((condition, RDF.type, SD.StrategicCondition))
        graph.add((condition, SD.aboutClass, ORG.Organization))
        graph.add((condition, RDFS.label, Literal(f"bench condition {index}")))
    return graph


def measure(graph: Graph, repeats: int = 5) -> dict:
    texts = {gate.stem: gate.read_text(encoding="utf-8") for gate in GATES}
    samples: dict[str, list[float]] = {stem: [] for stem in texts}
    rows: dict[str, int] = {}
    for _ in range(repeats):
        for stem, text in texts.items():
            started = time.perf_counter()
            result = list(graph.query(text))
            samples[stem].append(time.perf_counter() - started)
            rows[stem] = len(result)
    medians = {stem: round(statistics.median(values), 4) for stem, values in samples.items()}
    return {"median_seconds": medians, "total_seconds": round(sum(medians.values()), 4),
            "rows": rows, "repeats": repeats, "triples": len(graph)}


def gate_digests() -> dict[str, str]:
    return {gate.stem: hashlib.sha256(gate.read_bytes()).hexdigest() for gate in GATES}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="record benchmarks/receipt.json")
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    report = {
        "schema": "ggen.strategic-doctrine.gate-bench/1",
        "authority": "NONE",
        "gate_sha256": gate_digests(),
        "environment": {"python": platform.python_version(), "rdflib": rdflib.__version__,
                        "machine": platform.machine(), "system": platform.system(),
                        "load_average_1m": round(os.getloadavg()[0], 2)},
        "doctrine": measure(doctrine_graph(), args.repeats),
        "synthetic": {str(n): measure(synthetic_graph(n), args.repeats) for n in (16, 64)},
        "regression_bound": REGRESSION_BOUND,
    }
    report["per_gate_scale_ratio"] = {
        stem: round(report["synthetic"]["64"]["median_seconds"][stem]
                    / max(report["synthetic"]["16"]["median_seconds"][stem], 1e-6), 2)
        for stem in report["synthetic"]["64"]["median_seconds"]
    }
    report["per_gate_scale_violations"] = per_gate_scale_violations(
        report["synthetic"]["16"], report["synthetic"]["64"])
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write:
        RECEIPT.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
