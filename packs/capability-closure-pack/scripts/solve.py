#!/usr/bin/env python3
"""Closure/residual solver. Usage: solve.py REQUIREMENT.ttl [--index index/declared.ttl]

Loads ontology + index + requirement graph, refuses if any structural gate fires (gates/*.rq),
then runs queries/20-closure, 30-residual, 31-reuse and prints one JSON document:
  {reuse:[...], closure:[...], residual:[{id,reason,disposition,extend_from}], coverage:{...}}
Authority ceiling NONE: reads files, prints JSON, writes nothing.
"""
import argparse, json, sys
from pathlib import Path
from rdflib import Graph, Namespace

ROOT = Path(__file__).resolve().parents[1]
CC = Namespace("https://ggen.dev/ontology/capability-closure#")

def rows(g, name):
    return list(g.query((ROOT / "queries" / name).read_text(encoding="utf-8")))

def solve(requirement: Path, index: Path = ROOT / "index" / "declared.ttl") -> dict:
    g = Graph()
    for p in (ROOT / "ontology.ttl", index, requirement):
        g.parse(p, format="turtle")
    violations = []
    for gate in sorted((ROOT / "gates").glob("*.rq")):
        for r in g.query(gate.read_text(encoding="utf-8")):
            violations.append({"gate": gate.stem, "problem": str(r[0]), "detail": str(r[1])})
    if violations:
        return {"refusal": "REFUSED_GATE_ROWS", "violations": violations}
    reuse = [{"id": str(r.id), "pack": str(r.pack).rsplit(":", 1)[-1], "evidence": str(r.evidence)}
             for r in rows(g, "31-reuse.rq")]
    residual = [{"id": str(r.id), "reason": str(r.reason), "disposition": str(r.disposition),
                 "extend_from": str(r.extendFrom) if r.extendFrom else None}
                for r in rows(g, "30-residual.rq")]
    closure = sorted({str(r.depId) for r in rows(g, "20-closure.rq")})
    caps = {str(c) for c in g.objects(None, CC.id)} - {str(n) for n in g.objects(None, CC.id) if False}
    needs = {str(n) for r in g.subjects(CC.need, None) for n in g.objects(r, CC.need)}
    return {"reuse": reuse, "closure": closure, "residual": residual,
            "coverage": {"indexed_capabilities": len(list(g.subjects(CC.evidence, None))),
                         "needs": len(needs), "reuse": len(reuse), "residual": len(residual)}}

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("requirement", type=Path)
    ap.add_argument("--index", type=Path, default=ROOT / "index" / "declared.ttl")
    a = ap.parse_args()
    out = solve(a.requirement, a.index)
    print(json.dumps(out, indent=2, sort_keys=True))
    return 2 if "refusal" in out else 0

if __name__ == "__main__":
    sys.exit(main())
