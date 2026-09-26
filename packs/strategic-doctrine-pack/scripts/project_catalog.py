#!/usr/bin/env python3
"""Project the strategic doctrine graph into generated/catalog.json.

generated/catalog.json is a PROJECTION of ontology.ttl +
ontology/doctrine-33.ttl and is never edited by hand. It is the file the
autofde-lab boundary lab (and any other SELECT-only consumer) reads instead of
parsing RDF.

Usage:
    python3 scripts/project_catalog.py            # rewrite generated/catalog.json
    python3 scripts/project_catalog.py --stdout   # print the projection
    python3 scripts/project_catalog.py --check    # exit 1 if the file is stale

Determinism: entries are ordered by ordinal, primitive lists by step order,
falsifier lists by IRI; JSON is emitted with sorted keys, two-space indent and
a trailing newline. The projection embeds the sha256 of each input file, so a
change to the graph without a re-projection is detected by --check.

Authority: NONE. The projection selects; it never actuates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

PACK_ROOT = Path(__file__).resolve().parents[1]
INPUTS = ("ontology.ttl", "ontology/doctrine-33.ttl")
OUTPUT = PACK_ROOT / "generated" / "catalog.json"
SD = Namespace("https://ggen.dev/ontology/strategic-doctrine#")
CS_NONCLAIM = URIRef("urn:xaas:case-study:NonClaim")
SCHEMA = "ggen.strategic-doctrine-catalog/1"


def local(iri: URIRef) -> str:
    return str(iri).rsplit("#", 1)[-1]


def number(value: Literal) -> int | float:
    python = value.toPython()
    if isinstance(python, Decimal):
        return float(python)
    return python


def load_graph() -> Graph:
    graph = Graph()
    for relative in INPUTS:
        graph.parse(PACK_ROOT / relative, format="turtle")
    return graph


def input_digests() -> dict[str, str]:
    return {
        relative: hashlib.sha256((PACK_ROOT / relative).read_bytes()).hexdigest()
        for relative in INPUTS
    }


def falsifier_record(graph: Graph, falsifier: URIRef) -> dict[str, object]:
    observed = graph.value(falsifier, SD.observedProperty)
    window = graph.value(falsifier, SD.windowDays)
    threshold = graph.value(falsifier, SD.threshold)
    return {
        "comparator": str(graph.value(falsifier, SD.comparator)),
        "id": str(falsifier),
        "observed_property": local(observed) if observed is not None else None,
        "refuted_when": str(graph.value(falsifier, SD.refutedWhen)),
        "threshold": number(threshold) if threshold is not None else None,
        "window_days": number(window) if window is not None else None,
    }


def strategy_record(graph: Graph, strategy: URIRef) -> dict[str, object]:
    steps = sorted(
        graph.objects(strategy, SD.composedOf),
        key=lambda step: int(graph.value(step, SD.order)),
    )
    falsifiers = sorted(graph.objects(strategy, SD.hasFalsifier), key=str)
    return {
        "falsifiers": [falsifier_record(graph, falsifier) for falsifier in falsifiers],
        "id": str(strategy),
        "ordinal": int(graph.value(strategy, SD.ordinal)),
        "primitives": [local(graph.value(step, SD.operator)) for step in steps],
        "title": str(graph.value(strategy, SD.shortTitle)),
    }


def project() -> dict[str, object]:
    graph = load_graph()
    entries = set(graph.subjects(RDF.type, SD.Strategy)) | set(graph.subjects(RDF.type, SD.StrategyStub))
    strategies = sorted(
        (strategy_record(graph, entry) for entry in entries),
        key=lambda record: (record["ordinal"], record["id"]),
    )
    primitives = sorted(
        graph.subjects(RDF.type, SD.PrimitiveOperator),
        key=lambda primitive: int(graph.value(primitive, SD.ordinal)),
    )
    nonclaims = sorted(graph.subjects(RDF.type, CS_NONCLAIM), key=str)
    catalog = graph.value(predicate=RDF.type, object=SD.DoctrineCatalog)
    return {
        "authority": str(graph.value(catalog, SD.authority)),
        "authority_ceiling": str(graph.value(catalog, SD.authorityCeiling)),
        "inputs_sha256": input_digests(),
        "namespace": str(SD),
        "nonclaim": [
            {"id": str(nonclaim), "text": str(graph.value(nonclaim, RDFS.comment))}
            for nonclaim in nonclaims
        ],
        "primitives": [
            {
                "dual": local(dual) if (dual := graph.value(primitive, SD.dualOf)) is not None else None,
                "id": local(primitive),
                "ordinal": int(graph.value(primitive, SD.ordinal)),
            }
            for primitive in primitives
        ],
        "schema": SCHEMA,
        "strategies": strategies,
    }


def render() -> str:
    return json.dumps(project(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--stdout", action="store_true")
    args = parser.parse_args()

    text = render()
    if args.stdout:
        sys.stdout.write(text)
        return 0
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else None
        if current != text:
            print("REFUSED:CATALOG_PROJECTION_STALE:generated/catalog.json", file=sys.stderr)
            return 1
        print("catalog projection current: generated/catalog.json")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(PACK_ROOT).as_posix()} sha256:{hashlib.sha256(text.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
