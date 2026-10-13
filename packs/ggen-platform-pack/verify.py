#!/usr/bin/env python3
"""Real Chicago verifier: witness.ttl hash must match ontology/airo.ttl on disk.
Exit 0 iff the witnessed sw:syncedGraphHash equals the live sha256; else exit 1."""
import hashlib
import sys
from pathlib import Path

from rdflib import Graph

PACK_DIR = Path(__file__).resolve().parent
AIRO = PACK_DIR / "ontology" / "airo.ttl"


def main() -> int:
    witness = Graph()
    witness.parse(PACK_DIR / "witness.ttl", format="turtle")
    hashes = {
        str(o)
        for _, p, o in witness
        if str(p).endswith("#syncedGraphHash")
    }
    if len(hashes) != 1:
        print(f"REFUSED: expected exactly one witnessed hash, got {sorted(hashes)}")
        return 1
    witnessed = next(iter(hashes))

    if not AIRO.is_file():
        print(f"REFUSED: pinned ontology missing: {AIRO}")
        return 1
    live = hashlib.sha256(AIRO.read_bytes()).hexdigest()
    if live != witnessed:
        print(f"REFUSED: witness hash drift (witness={witnessed} live={live})")
        return 1

    gates = {p.name for p in (PACK_DIR / "gates").glob("*.rq")}
    witnessed_gates = {
        str(o)
        for _, p, o in witness
        if str(p).endswith("#gate") and str(o).endswith(".rq")
    }
    if witnessed_gates != gates:
        print(f"REFUSED: gate-set mismatch (witnessed={sorted(witnessed_gates)} "
              f"on-disk={sorted(gates)})")
        return 1

    print(f"OK: airo.ttl matches witness pin {witnessed[:12]}...; "
          f"{len(gates)} gate(s) witnessed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
