#!/usr/bin/env python3
"""Validate an OCEL-projected actuation data graph against the real Level-4
causal-chain SHACL shapes (ontology/level4-chain.shacl.ttl), by running pyshacl.

These shapes are the only expression of the Level-4 constraints -- see the
header comment of ontology/level4-chain.shacl.ttl. This gate does not
re-implement any of that logic in Python; it loads the data graph, loads the
committed shapes graph, and calls pyshacl.validate() for real.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

try:
    from rdflib import Graph
except ModuleNotFoundError as exc:
    print(json.dumps({"standing": "UNSUPPORTED", "reason": "rdflib is required", "error": str(exc)}))
    raise SystemExit(3)

try:
    import pyshacl
except ModuleNotFoundError as exc:
    print(json.dumps({"standing": "UNSUPPORTED", "reason": "pyshacl is required", "error": str(exc)}))
    raise SystemExit(3)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "qualification" / "consumer.ttl",
        help="OCEL-projected data graph to validate (default: qualification/consumer.ttl)",
    )
    args = parser.parse_args()

    pack_root = Path(__file__).resolve().parents[1]
    shapes_path = pack_root / "ontology" / "level4-chain.shacl.ttl"
    data_path = args.data

    data_graph = Graph()
    try:
        data_graph.parse(data_path, format="turtle")
    except Exception as exc:
        print(json.dumps({"conforms": False, "violations": [], "error": f"failed to parse data graph {data_path}: {exc}"}))
        return 2

    shapes_graph = Graph()
    try:
        shapes_graph.parse(shapes_path, format="turtle")
    except Exception as exc:
        print(json.dumps({"conforms": False, "violations": [], "error": f"failed to parse shapes graph {shapes_path}: {exc}"}))
        return 2

    conforms, results_graph_raw, _ = pyshacl.validate(
        data_graph,
        shacl_graph=shapes_graph,
        data_graph_format="turtle",
        shacl_graph_format="turtle",
        inference="none",
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
        meta_shacl=False,
        advanced=True,
        js=False,
    )
    # pyshacl.validate()'s return type is declared as a broad union across its
    # overloads; with our fixed kwargs (no do_owl_imports serialization path)
    # the middle element is always the real results Graph -- cast so
    # .subjects()/.objects() type-check without re-implementing pyshacl's logic.
    results_graph = cast(Graph, results_graph_raw)

    violations = []
    SH = "http://www.w3.org/ns/shacl#"

    from rdflib.namespace import RDF as _RDF
    from rdflib import URIRef as _URIRef

    for subject in results_graph.subjects(_RDF.type, _URIRef(SH + "ValidationResult")):
        def one(pred):
            values = list(results_graph.objects(subject, _URIRef(SH + pred)))
            return str(values[0]) if values else None

        violations.append(
            {
                "focusNode": one("focusNode"),
                "resultPath": one("resultPath"),
                "value": one("value"),
                "sourceShape": one("sourceShape"),
                "sourceConstraintComponent": one("sourceConstraintComponent"),
                "resultMessage": one("resultMessage"),
                "resultSeverity": one("resultSeverity"),
            }
        )

    payload = {
        "conforms": bool(conforms),
        "data_graph": str(data_path),
        "shapes_graph": str(shapes_path),
        "violation_count": len(violations),
        "violations": violations,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))

    return 0 if conforms else 1


if __name__ == "__main__":
    raise SystemExit(main())
