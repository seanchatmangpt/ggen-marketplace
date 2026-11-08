#!/usr/bin/env python3
"""010_ttl_triple_counts.py — generalized TTL triple-count court.

Generalization of srve's scripts/ttl_court.py (J14, wave R155): baselines,
required terms, and graph paths move from hardcoded constants to a TOML
config file, so any repo can pin its own baselines without editing the gate.

Config format (TOML, default: baselines.toml next to this script):

    namespace = "http://onengine.dev/ontology#"

    [[graphs]]
    name = "finance"
    path = "ontology/finance.ttl"   # relative to --root (default: config dir)
    triples = 280                   # expected rdflib triple count

    [[terms]]                        # optional, repeatable
    uri = "http://onengine.dev/ontology#APBill"

Exit codes: 0 = all counts match and all terms present; 1 = any drift,
parse error, missing file, or missing term. 2 = config/usage error.
"""

import argparse
import os
import sys
import tomllib

from rdflib import Graph

DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "baselines.toml")


def load_config(path):
    with open(path, "rb") as fh:
        cfg = tomllib.load(fh)
    if not isinstance(cfg.get("graphs"), list) or not cfg["graphs"]:
        print(f"CONFIG-ERROR {path}: missing/empty [[graphs]] table")
        sys.exit(2)
    for g in cfg["graphs"]:
        for key in ("name", "path", "triples"):
            if key not in g:
                print(f"CONFIG-ERROR {path}: graph {g!r} missing '{key}'")
                sys.exit(2)
    return cfg


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=DEFAULT_CONFIG, help="TOML config path")
    ap.add_argument("--root", default=None,
                    help="base dir for graph paths (default: config file's dir)")
    args = ap.parse_args()

    cfg = load_config(args.config)
    root = args.root or os.path.dirname(os.path.abspath(args.config))

    rc = 0
    union = set()
    for entry in cfg["graphs"]:
        path = entry["path"] if os.path.isabs(entry["path"]) else os.path.join(root, entry["path"])
        expected = entry["triples"]
        if not os.path.isfile(path):
            print(f"FAIL {path}: missing file")
            rc = 1
            continue
        try:
            g = Graph().parse(path, format="turtle")
        except Exception as exc:
            print(f"FAIL {path}: parse error: {exc}")
            rc = 1
            continue
        union |= set(g)
        n = len(g)
        status = "OK" if n == expected else "DRIFT"
        rc |= n != expected
        print(f"{status:5} {path}: actual={n} expected={expected}")

    namespace = cfg.get("namespace", "")
    for term in cfg.get("terms", []):
        uri = term["uri"]
        found = any(uri in (str(s), str(p), str(o)) for s, p, o in union)
        status = "OK" if found else "MISSING"
        rc |= not found
        print(f"{status:7} term {uri}")
    if "namespace" in cfg and cfg.get("terms"):
        print(f"note: namespace {namespace} (terms are matched as full URIs)")

    if rc == 0:
        print("COURT: PASS — all triple counts match baselines, all terms present")
    else:
        print("COURT: FAIL — drift detected (see above)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
