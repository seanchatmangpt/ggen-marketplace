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

    # Shared-head KAT court (lane L9): recompute the logchain head from the
    # pack's own witnessed fixture entries and assert equality with the
    # pinned cross-repo KAT literal — the same chain head insa-proof's sync
    # replay law and strata-protocol's logchain law both fold to
    # (h = blake3(h_prev || pn_be || ocel_be || tick_be64), GENESIS = 32*0x00,
    # tick = top byte of the OCEL word widened to u64 big-endian).
    import blake3

    KAT_HEAD = "05ea1aa096f45968aacb2c996d2b541e4b9fdef24f006e0204e1fa88d33f68a5"

    def _step(h: bytes, pn: int, ocel: int) -> bytes:
        tick = ocel >> 56
        return blake3.blake3(
            h + pn.to_bytes(8, "big") + ocel.to_bytes(8, "big") + tick.to_bytes(8, "big")
        ).digest()

    kat_entries: list = []
    pn_map: dict = {}
    ocel_map: dict = {}
    for s, p, o in witness:
        pred = str(p)
        if pred.endswith("#pn"):
            pn_map[s] = int(str(o), 16)
        elif pred.endswith("#ocel"):
            ocel_map[s] = int(str(o), 16)
    for s, pn in pn_map.items():
        if s in ocel_map:
            kat_entries.append((pn, ocel_map[s]))
    kat_entries.sort()

    kat_head_witnessed = next(
        (
            str(o)
            for s, p, o in witness
            if str(p).endswith("#sharedKatHead")
        ),
        None,
    )

    if not kat_entries or kat_head_witnessed is None:
        print("REFUSED: shared-head KAT witnesses missing (entries or pinned head)")
        return 1
    if kat_head_witnessed.lower() != KAT_HEAD:
        print(
            f"REFUSED: witnessed KAT head drift (witness={kat_head_witnessed} "
            f"court={KAT_HEAD})"
        )
        return 1
    computed = bytes.fromhex("00" * 32)
    for pn, ocel in kat_entries:
        computed = _step(computed, pn, ocel)
    if computed.hex() != KAT_HEAD:
        print(
            f"REFUSED: shared-head KAT divergence (computed={computed.hex()} "
            f"pinned={KAT_HEAD})"
        )
        return 1
    print(f"PASS shared-head-kat: recomputed head {computed.hex()} == pinned KAT over {len(kat_entries)} entries")

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
    print("OK: all gates zero-rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
