#!/usr/bin/env python3
"""Verifier gate (outside the .rq court): every cc:evidence path in the index must exist under
packs/. Exit 0 ALIVE, 2 REFUSED with the missing paths. A provides claim with no file is a
claim, not a capability."""
import json, sys
from pathlib import Path
from rdflib import Graph, Namespace

CC = Namespace("https://ggen.dev/ontology/capability-closure#")
PACKS = Path(__file__).resolve().parents[2]
INDEX = Path(__file__).resolve().parents[1] / "index" / "declared.ttl"

def main() -> int:
    g = Graph(); g.parse(INDEX, format="turtle")
    missing = sorted(str(p) for p in g.objects(None, CC.evidence) if not (PACKS / str(p)).is_file())
    total = len(set(g.objects(None, CC.evidence)))
    if missing:
        print(json.dumps({"refusal": "REFUSED_EVIDENCE_PATH_MISSING", "missing": missing}), file=sys.stderr)
        return 2
    print(json.dumps({"observed": "ALIVE", "evidence_paths": total}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
