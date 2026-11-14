#!/usr/bin/env python3
"""Gate runner for gcp-marketplace-saas-pack: SELECT gates over a data graph.

Zero rows = pass, any row = refusal. Default data graph is ../ontology.ttl;
`--witnesses` additionally runs every gate against witnesses/pass (must be
zero rows) and witnesses/fail (must be >=1 row), proving non-vacuity.
Exit 0 all pass, 1 refusal / witness violation.
"""
import argparse
import glob
import os
import sys

from rdflib import Graph

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)


def gate_paths():
    return sorted(glob.glob(os.path.join(HERE, "*.rq")))


def rows_for(gate_path, data_path):
    g = Graph()
    g.parse(data_path, format="turtle")
    with open(gate_path, encoding="utf-8") as fh:
        return list(g.query(fh.read()))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ontology", default=os.path.join(PACK, "ontology.ttl"))
    ap.add_argument("--witnesses", action="store_true")
    args = ap.parse_args(argv)
    bad = []
    for path in gate_paths():
        stem = os.path.splitext(os.path.basename(path))[0]
        rows = rows_for(path, args.ontology)
        print(f"{stem}: {'PASS' if not rows else 'FAIL'} ({len(rows)} rows)")
        if rows:
            bad.append(stem)
        if args.witnesses:
            p = rows_for(path, os.path.join(PACK, "witnesses", "pass", stem + ".ttl"))
            f = rows_for(path, os.path.join(PACK, "witnesses", "fail", stem + ".ttl"))
            print(f"  witness pass rows={len(p)} fail rows={len(f)}")
            if p or not f:
                bad.append(stem + ":witness")
    if bad:
        print("GATE_REFUSAL: " + ", ".join(bad))
        return 1
    print("ALL_GATES_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
