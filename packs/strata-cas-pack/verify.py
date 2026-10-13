#!/usr/bin/env python3
"""Real Chicago verifier: re-run every gates/*.rq SELECT against ontology.ttl.
Exit 0 iff every gate returns zero rows (violation-free); else print and exit 1."""
import sys
from pathlib import Path

from rdflib import Graph

PACK_DIR = Path(__file__).resolve().parent


def main() -> int:
    graph = Graph()
    graph.parse(PACK_DIR / "ontology.ttl", format="turtle")

    # Gate-set assertion: executed gates must match the witnessed sw:GateRun set.
    witness = Graph()
    witness.parse(PACK_DIR / "witness.ttl", format="turtle")
    witnessed = {
        str(o)
        for s, p, o in witness
        if str(p).endswith("#gate") and str(o).endswith(".rq")
    }
    on_disk = {p.name for p in (PACK_DIR / "gates").glob("*.rq")}
    if witnessed != on_disk:
        missing = sorted(witnessed - on_disk)
        extra = sorted(on_disk - witnessed)
        print("REFUSED: gate-set mismatch")
        if missing:
            print(f"  witnessed-but-missing: {missing}")
        if extra:
            print(f"  on-disk-but-unwitnessed: {extra}")
        return 1

    violations = 0
    for gate in sorted((PACK_DIR / "gates").glob("*.rq")):
        query = gate.read_text(encoding="utf-8")
        rows = list(graph.query(query))
        if rows:
            violations += len(rows)
            print(f"VIOLATION {gate.name}: {len(rows)} row(s)")
            for row in rows:
                print(f"  {tuple(str(cell) for cell in row)}")
        else:
            print(f"PASS {gate.name}: 0 rows")

    if violations:
        print(f"FAIL: {violations} violation row(s)")
        return 1
    print("OK: all gates zero-rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
