#!/usr/bin/env python3
"""Validate campaign WORKGRAPH.ttl / goal.ttl graphs against the
ggen_igniter semantic-jira-pack work-order SHACL shapes (pyshacl).

For each target graph, reports conforms true/false, per-shape violation
counts, and a classification: doc-graph style mismatch (e.g. GoalCheckpoint
goal graphs or doc-graph WorkOrders that intentionally omit the execution
order court fields) versus lexical/enum defects (bad SHA format, bad
standing/receiptClass enum, duplicate identifiers).

Usage:
    python3 scripts/validate_workgraphs.py            # table + classification
    python3 scripts/validate_workgraphs.py --markdown # also emit report body
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, URIRef

HOME = Path.home()
PACK_SHAPES = HOME / "ggen_igniter/priv/ggen/semantic-jira-pack/shapes"
SHAPES = PACK_SHAPES / "work-order.shacl.ttl"
GC_SHAPES = PACK_SHAPES / "goal-checkpoint.shacl.ttl"

TARGETS = [
    # (repo, graph path)
    ("ash_a2a", "ash_a2a/docs/sjira/v26.10.8/WORKGRAPH.ttl"),
    ("ash_affidavit", "ash_affidavit/docs/sjira/v26.10.8/WORKGRAPH.ttl"),
    ("ash_pplan", "ash_pplan/docs/sjira/v26.10.8-1/WORKGRAPH.ttl"),
    ("ash_r2rml", "ash_r2rml/docs/sjira/v26.10.8/WORKGRAPH.ttl"),
    ("ash_surface", "ash_surface/docs/sjira/v26.10.8/WORKGRAPH.ttl"),
    ("beam4pm", "beam4pm/docs/sjira/v26.10.8/WORKGRAPH.ttl"),
    ("castle", "castle/docs/sjira/v26.10.8/goal.ttl"),
    ("ex4pm", "ex4pm/docs/sjira/v26.10.8/WORKGRAPH.ttl"),
    ("ggen-ecosystem", "ggen-ecosystem/docs/sjira/v26.10.8/WORKGRAPH.ttl"),
    ("ggen-marketplace", "ggen-marketplace/docs/sjira/v26.10.8/WORKGRAPH.ttl"),
    ("xaas", "xaas/docs/sjira/v26.10.8/WORKGRAPH.ttl"),
    ("zcode-cli", "zcode-cli/docs/sjira/v26.10.8/WORKGRAPH.ttl"),
]

SJ = "https://ggen-igniter.dev/ontology/semantic-jira#"
# Violation-message fragments that are inherent to doc-graph / goal-graph
# style rather than defects in the authored data. Doc-graphs (and goal graphs
# authored in sj:GoalCheckpoint style) intentionally omit the execution-order
# court fields, cite receipts outside the graph, and use graph-local
# documentation properties.
STYLE_FRAGMENTS = [
    "ALIVE requires exact candidate/subject SHA",          # doc graphs cite commits, not receipts
    "ALIVE requires an independent court",                 # same law, GlobalIntegrity form
    "Authority-requiring work must bind authority",        # doc graphs use prose authority notes
    "origin authority carries no admission witness",       # doc graphs name sources, not admitted authorities
    "origin is not code-work authority",                   # same origin law, type form
    "is closed. It cannot have value",                     # graph-local doc properties (wg:/eco:/prov: ...)
    "Value is not of Node Kind sh:IRI",                    # literals where the pack expects IRIs
    "Value does not have class",                           # literals where the pack expects typed classes
    "Less than 1 values",                                  # execution-order fields docs graphs omit
    "requires sj:courtCommand",                            # goal-graph checkpoint tuple fields
    "requires sj:boundaryClass",
    "requires sj:stopQuery",
]
# Fragments that indicate a lexical or referential defect in the data itself.
DEFECT_FRAGMENTS = [
    ("does not match pattern", "pattern-violation"),
    ("must be unique across", "uniqueness"),
    ("More than 1 values", "cardinality"),
    ("must not be its own parent", "cycle"),
]

SQ = re.compile(r"Focus Node: (\S+)|Message: ([^\n]+)")


def classify(message: str) -> str:
    for frag in STYLE_FRAGMENTS:
        if frag in message:
            return "style-mismatch"
    for frag, label in DEFECT_FRAGMENTS:
        if frag in message:
            return label
    return "unclassified"


def load_graph(path: Path) -> Graph:
    g = Graph()
    g.parse(path, format="turtle")
    return g


def run_one(repo: str, rel: str) -> dict:
    path = HOME / rel
    if not path.exists():
        return {"repo": repo, "path": str(path), "missing": True}
    data = load_graph(path)
    # Goal-graph style detection: a graph whose subjects are (exclusively)
    # sj:GoalCheckpoint nodes is a goal.ttl-style doc graph — validate it
    # against the closed GoalCheckpoint shape, not the work-order shape.
    rdf_type = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    wo = set(data.subjects(rdf_type, URIRef(f"{SJ}WorkOrder")))
    gc = set(data.subjects(rdf_type, URIRef(f"{SJ}GoalCheckpoint")))
    shape_path = GC_SHAPES if (gc and not wo) else SHAPES
    shapes = load_graph(shape_path)
    conforms, results_graph, results_text = validate(
        data_graph=data,
        shacl_graph=shapes,
        inference="none",
        advanced=True,
        debug=False,
    )
    violations = []
    # Extract (focus node, path, value, message) tuples from the text report.
    focus = path_ = value = None
    for line in results_text.splitlines():
        line = line.strip()
        if line.startswith("Focus Node:"):
            focus = line.split(":", 1)[1].strip()
        elif line.startswith("Result Path:"):
            path_ = line.split(":", 1)[1].strip()
        elif line.startswith("Value:"):
            value = line.split(":", 1)[1].strip()
        elif line.startswith("Message:"):
            msg = line.split(":", 1)[1].strip()
            violations.append((focus, path_, value, msg))
            focus = path_ = value = None
    counts = Counter(classify(msg) for *_, msg in violations)
    return {
        "repo": repo,
        "path": str(path),
        "shapes": str(shape_path),
        "conforms": bool(conforms),
        "violations": violations,
        "class_counts": dict(counts),
        "work_orders": len(wo),
        "goal_checkpoints": len(gc),
        "missing": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    results = [run_one(repo, rel) for repo, rel in TARGETS]

    print(f"shapes: {SHAPES}")
    print()
    hdr = f"{'repo':<18} {'conforms':<9} {'WO':>4} {'GC':>4}  classes"
    print(hdr)
    print("-" * len(hdr))
    for r in results:
        if r.get("missing"):
            print(f"{r['repo']:<18} MISSING    {r['path']}")
            continue
        classes = ", ".join(
            f"{k}={v}" for k, v in sorted(r["class_counts"].items())
        ) or "none"
        print(
            f"{r['repo']:<18} {str(r['conforms']):<9} "
            f"{r['work_orders']:>4} {r['goal_checkpoints']:>4}  {classes}"
        )

    if args.json_out:
        import json

        args.json_out.write_text(
            json.dumps(
                [
                    {k: v for k, v in r.items() if k != "violations"}
                    | {
                        "violations": [
                            {"focus": f, "path": p, "value": v, "message": m}
                            for f, p, v, m in r.get("violations", [])
                        ]
                    }
                    for r in results
                ],
                indent=2,
            )
        )

    if args.markdown:
        print()
        print("## Markdown detail")
        for r in results:
            if r.get("missing"):
                continue
            print(f"\n### {r['repo']} ({r['path']})")
            print(f"conforms: {r['conforms']}")
            for focus, vpath, value, msg in r["violations"]:
                short = focus.rsplit("#", 1)[-1].rsplit("/", 1)[-1] if focus else "?"
                print(f"- [{classify(msg)}] {short} path={vpath} value={value}")
                print(f"  msg: {msg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
