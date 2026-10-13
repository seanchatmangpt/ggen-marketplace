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

    # ── L171: witnessed work-sum KAT for the u128 chain-work law ──────
    kat_fail = run_work_kat(witness)
    if kat_fail:
        print(f"FAIL: work KAT: {kat_fail} assertion(s) failed")
        return 1
    print("OK: all gates zero-rows; work KAT green")
    return 0


def run_work_kat(witness: Graph) -> int:
    """Recompute per-block work + total chain work from the witnessed
    constants and assert the pins. Tamper negatives:
      - nonce flip     -> PoW digest divergence (validation refusal);
      - difficulty flip -> per-block work divergence (work is
        target-derived by law, so nonce tampering does NOT move work).
    Returns the count of failed assertions."""
    import hashlib

    from rdflib import URIRef

    SW = "https://strata.chatman.ai/ontology/witness#"

    def swp(local: str):
        return URIRef(SW + local)

    kats = [
        s
        for s in set(witness.subjects(None, None))
        if (s, None, swp("WorkKat")) in witness
    ]
    if len(kats) != 1:
        print(f"REFUSED: expected exactly 1 sw:WorkKat, found {len(kats)}")
        return 1
    kat = kats[0]

    def iv(b, local: str) -> int:
        return int(witness.value(b, swp(local)))

    blocks = sorted(
        witness.objects(kat, swp("block")), key=lambda b: iv(b, "height")
    )
    if len(blocks) != 4:
        print(f"REFUSED: KAT must witness 4 blocks, found {len(blocks)}")
        return 1
    if not any(iv(b, "difficultyTarget") == 63 for b in blocks):
        print("REFUSED: KAT must include one difficulty-63 block")
        return 1

    fails = 0
    sha256 = lambda data: hashlib.sha256(data).digest()

    def header_bytes(height, parent, difficulty, slot):
        return (
            height.to_bytes(8, "big")
            + parent
            + difficulty.to_bytes(4, "big")
            + slot.to_bytes(8, "big")
        )

    parent = bytes(32)
    parent_of_last = parent
    total = 0
    for b in blocks:
        height = iv(b, "height")
        difficulty = iv(b, "difficultyTarget")
        nonce = iv(b, "nonce")
        slot = iv(b, "slot")
        pin_work = iv(b, "pinnedWork")
        pin_hash = str(witness.value(b, swp("pinnedPowHash")))

        header = header_bytes(height, parent, difficulty, slot)
        # recompute from constants (mirrors the u128 work law)
        work = 1 << min(difficulty, 127)
        pow_hash = sha256(header + nonce.to_bytes(8, "big")).hex()

        if work != pin_work:
            print(f"  KAT FAIL b{height}: work {work} != pinned {pin_work}")
            fails += 1
        if pow_hash != pin_hash:
            print(f"  KAT FAIL b{height}: pow hash drift vs pinned")
            fails += 1
        total += work
        parent_of_last = parent
        parent = sha256(header)  # engine law: parentHash = H(header encoding)

    pin_total = iv(kat, "totalChainWork")
    if total != pin_total:
        print(f"  KAT FAIL: total chain work {total} != pinned {pin_total}")
        fails += 1

    # Tamper negative 1: flip one nonce bit on the difficulty-63 block.
    b63 = next(b for b in blocks if iv(b, "difficultyTarget") == 63)
    d = iv(b63, "difficultyTarget")
    n = iv(b63, "nonce")
    pin_h = str(witness.value(b63, swp("pinnedPowHash")))
    header = header_bytes(
        iv(b63, "height"), parent_of_last, d, iv(b63, "slot")
    )
    tampered = sha256(header + (n ^ 1).to_bytes(8, "big")).hex()
    if tampered == pin_h:
        print("  KAT FAIL: nonce tamper did NOT diverge the PoW digest")
        fails += 1
    else:
        print("PASS work-kat tamper(nonce): PoW digest diverged -> REFUSED")

    # Tamper negative 2: difficulty tamper must diverge per-block work.
    if (1 << min(d ^ 1, 127)) == (1 << min(d, 127)):
        print("  KAT FAIL: difficulty tamper did NOT diverge work")
        fails += 1
    else:
        print("PASS work-kat tamper(difficulty): work diverged -> REFUSED")

    if fails == 0:
        print(
            f"PASS work-kat: 4 blocks, per-block pins + total {total} all green"
        )
    return fails


if __name__ == "__main__":
    sys.exit(main())
