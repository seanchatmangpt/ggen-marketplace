#!/usr/bin/env python3
"""Witness court for industry-aero-defense (exact-stem)."""
import json, sys
from pathlib import Path
try:
    from rdflib import Graph
except ImportError:
    raise SystemExit("REFUSED:VERIFIER_UNAVAILABLE:rdflib")

ROOT = Path(__file__).resolve().parents[1]
GATES = sorted((ROOT / "gates").glob("*.rq"), key=lambda p: p.name)
PASS = ROOT / "witnesses/pass"
FAIL = ROOT / "witnesses/fail"
SCHEMA = "ggen.marketplace.aero-defense-court/1"


def rows_for(graph, gate):
    res = graph.query(gate.read_text(encoding="utf-8"))
    return [{str(v): str(row[v]) for v in res.vars} for row in res]


def main():
    failures = []
    for gate in GATES:
        stem = gate.stem
        pass_w = PASS / f"{stem}.ttl"
        fail_w = FAIL / f"{stem}.ttl"
        if not pass_w.is_file():
            failures.append(f"pass-witness-missing:{stem}"); continue
        if not fail_w.is_file():
            failures.append(f"fail-witness-missing:{stem}"); continue
        g = Graph()
        g.parse(ROOT / "ontology.ttl", format="turtle")
        g.parse(pass_w, format="turtle")
        if rows_for(g, gate):
            failures.append(f"pass-witness-fired:{stem}")
        fg = Graph()
        fg.parse(ROOT / "ontology.ttl", format="turtle")
        fg.parse(fail_w, format="turtle")
        if not rows_for(fg, gate):
            failures.append(f"fail-witness-silent:{stem}")
    report = {"schema": SCHEMA, "gate_count": len(GATES), "failures": failures,
              "standing": "ALIVE" if not failures else "REFUSED"}
    print(json.dumps(report, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
