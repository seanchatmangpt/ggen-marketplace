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

    # BLAKE3 KAT court (lane L194, post-L167 consolidation): the pack owns the
    # canonical BLAKE3, so verify pins spec vectors, not just gate row-counts.
    # Witness pins BLAKE3("") — the spec empty-input vector — plus one
    # canonical fold input/output over the pack's own namespace. Recomputed
    # here with the real `b3sum` binary (Python hashlib has no blake3;
    # provenance: /opt/homebrew/bin/b3sum, Homebrew BLAKE3 core team build,
    # cross-checkable against the BLAKE3 reference test suite).
    import shutil
    import subprocess

    B3SUM = shutil.which("b3sum")
    if B3SUM is None:
        print("REFUSED: b3sum binary not on PATH; BLAKE3 KAT unverifiable")
        return 1

    def _b3sum(data: bytes) -> str:
        res = subprocess.run([B3SUM], input=data, capture_output=True)
        if res.returncode != 0:
            print(f"REFUSED: b3sum failed: {res.stderr.decode(errors='replace')}")
            return ""
        return res.stdout.decode().split()[0].strip().lower()

    def _w1(pred_suffix: str) -> str | None:
        return next(
            (
                str(o)
                for s, p, o in witness
                if str(p).endswith(pred_suffix)
            ),
            None,
        )

    kat_empty = _w1("#katEmptyInputDigest")
    kat_fold_in = _w1("#katFoldInput")
    kat_fold = _w1("#katFoldDigest")
    if not (kat_empty and kat_fold_in and kat_fold):
        print("REFUSED: BLAKE3 KAT witnesses missing (empty digest, fold input, fold digest)")
        return 1

    computed_empty = _b3sum(b"")
    if computed_empty != kat_empty.lower():
        print(
            f"REFUSED: BLAKE3 KAT divergence on empty input "
            f"(computed={computed_empty} pinned={kat_empty})"
        )
        return 1
    computed_fold = _b3sum(kat_fold_in.encode("utf-8"))
    if computed_fold != kat_fold.lower():
        print(
            f"REFUSED: BLAKE3 KAT divergence on fold input "
            f"(computed={computed_fold} pinned={kat_fold})"
        )
        return 1
    print(
        "PASS blake3-kat: BLAKE3(\"\") and canonical fold recomputed via b3sum "
        "match witnessed pins"
    )

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
