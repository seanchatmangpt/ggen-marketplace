#!/usr/bin/env python3
"""Real Chicago verifier: re-run every gates/*.rq SELECT against ontology.ttl.
Exit 0 iff every gate returns zero rows (violation-free); else print and exit 1."""
import sys
from pathlib import Path

from typing import Iterable, cast

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

    # Witness-hash assertion: the committed pack-level sw:syncedGraphHash must
    # match the local runtime receipt's payload.graph_hash when one exists.
    pack_level = {
        str(o)
        for s, p, o in witness
        if str(p).endswith("#syncedGraphHash")
        if any(str(q).endswith("#pack") for _, q, _ in witness.triples((s, None, None)))
    }
    receipt_path = PACK_DIR / ".ggen-v2" / "receipt.json"
    if not receipt_path.exists():
        print("NOTE: no local receipt; witness hashes not re-verified")
    else:
        import json

        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt_hash = receipt.get("payload", {}).get("graph_hash")
        if len(pack_level) != 1 or not receipt_hash or pack_level != {receipt_hash}:
            witness_hash = next(iter(pack_level), None)
            print(
                f"REFUSED: witness hash drift (witness={witness_hash} "
                f"receipt={receipt_hash})"
            )
            return 1

    violations = 0
    for gate in sorted((PACK_DIR / "gates").glob("*.rq")):
        query = gate.read_text(encoding="utf-8")
        # rdflib types Result.__iter__ as Iterator[Union[_TripleType, bool,
        # ResultRow]]; SELECT rows are always iterable tuples, so narrow via cast.
        rows = list(cast(Iterable[tuple], graph.query(query)))
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

    # Pinned cross-pack court: the pinned copy of the valve projection
    # (pinned/strata-valve-refusals.ex) must carry a sha256 header pin,
    # its body (bytes after the header) must hash to that pin, and the
    # live valve projection must hash to the same pin when present.
    import hashlib
    import re

    pin_path = PACK_DIR / "pinned" / "strata-valve-refusals.ex"
    if not pin_path.exists():
        print("REFUSED: pinned valve copy missing (pinned/strata-valve-refusals.ex)")
        return 1
    raw = pin_path.read_bytes()
    m = re.search(rb"sha256=([0-9a-f]{64})", raw)
    if not m:
        print("REFUSED: pinned valve copy has no sha256 header pin")
        return 1
    pin = m.group(1).decode()
    body = raw.split(b"\n", 2)[2]
    body_hash = hashlib.sha256(body).hexdigest()
    if body_hash != pin:
        print(f"REFUSED: pinned valve body hash {body_hash} != header pin {pin}")
        return 1
    live = PACK_DIR.parent / "strata-valve-pack" / "generated" / "refusals.ex"
    if live.exists():
        live_hash = hashlib.sha256(live.read_bytes()).hexdigest()
        if live_hash != pin:
            print(f"REFUSED: live valve refusals.ex hash {live_hash} != pin {pin}")
            return 1
        print(f"PASS pinned-valve-copy: sha256 pin {pin} matches body and live valve projection")
    else:
        print(f"NOTE: live valve projection absent; pinned body verified against pin {pin}")

    print("OK: all gates zero-rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
