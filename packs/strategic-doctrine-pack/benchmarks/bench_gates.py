#!/usr/bin/env python3
"""Deterministic latency benchmark for the six strategic-doctrine gates.

Measures wall time of every gate in gates/ (real rdflib SPARQL engine, real
query text) over:
  - the shipped doctrine graph (ontology + world model + 33-entry catalog +
    entrant-world fixture), and
  - synthetic doctrine graphs of N operationalized strategies (4 ordered
    steps, one falsifier, one condition, one objective each), built from own
    placeholder text only, used to bound growth as the catalog scales.

Usage:
    python3 benchmarks/bench_gates.py --write     # re-record benchmarks/receipt.json
    python3 benchmarks/bench_gates.py             # print a fresh measurement

The receipt carries a regression bound consumed by
tests/test_strategic_doctrine_pack_hardening.py: each gate's observed median
must stay within max(recorded * factor, floor_seconds), and the synthetic
64-strategy total within scale_4x_factor of the 16-strategy total.
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
REGRESSION_BOUND = {"factor": 5.0, "floor_seconds": 2.0, "scale_4x_factor": 8.0}


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
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write:
        RECEIPT.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
