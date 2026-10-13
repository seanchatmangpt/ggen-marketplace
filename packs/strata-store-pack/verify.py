#!/usr/bin/env python3
"""Real Chicago verifier: re-run every gates/*.rq SELECT against ontology.ttl.
Exit 0 iff every gate returns zero rows (violation-free); else print and exit 1.
(Chicago pattern shared with strata-pn64-pack/verify.py — no mocks, real graph,
real query execution; the gate .rq files are the only authority.)
"""
import sys
from pathlib import Path

from typing import Iterable, cast

from rdflib import Graph

PACK_DIR = Path(__file__).resolve().parent


def main() -> int:
    graph = Graph()
    graph.parse(PACK_DIR / "ontology.ttl", format="turtle")

    # Gate-set assertion (L27 pattern, strata-chain-pack parity): executed
    # gates must match the witnessed sw:GateRun set.
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

    # Content-address KAT court (lane L170, witnessed-replay pattern from
    # strata-chain-pack): recompute each witnessed entry's content address
    # from its payload with the store's own law (key == SHA-256(value)),
    # fold the store root exactly as InMemoryStore::root_digest does
    # (SHA-256 over the concatenated keys in BTreeMap lexicographic byte
    # order), and assert equality with the pinned sw:storeKatRoot literal.
    # Digests were derived by running the pack's generated module via a
    # rustc driver (/tmp/store-kat) — never invented.
    import hashlib

    def _hexbytes(s: str) -> bytes:
        t = s.strip().lower()
        if t.startswith("0x"):
            t = t[2:]
        return bytes.fromhex(t)

    payloads: dict = {}
    digests: dict = {}
    for s, p, o in witness:
        pred = str(p)
        if pred.endswith("#katPayload"):
            payloads[s] = str(o).encode("utf-8")
        elif pred.endswith("#katDigest"):
            digests[s] = _hexbytes(str(o))
    kat_entries = sorted(
        (s for s in payloads if s in digests), key=str
    )
    pinned_root = next(
        (
            str(o)
            for s, p, o in witness
            if str(p).endswith("#storeKatRoot")
        ),
        None,
    )
    if not kat_entries or pinned_root is None:
        print("REFUSED: content-address KAT witnesses missing (entries or pinned root)")
        return 1

    recomputed: dict = {}
    for s in kat_entries:
        recomputed[s] = hashlib.sha256(payloads[s]).digest()
        if recomputed[s] != digests[s]:
            print(
                f"REFUSED: content-address divergence for {s} "
                f"(computed={recomputed[s].hex()} witnessed={digests[s].hex()})"
            )
            return 1
    in_key_order = sorted(kat_entries, key=lambda s: recomputed[s])
    folded = hashlib.sha256(b"".join(recomputed[s] for s in in_key_order)).hexdigest()
    if folded != pinned_root.lower():
        print(
            f"REFUSED: store root divergence (computed={folded} "
            f"pinned={pinned_root})"
        )
        return 1
    print(
        f"PASS content-address-kat: {len(kat_entries)} addresses recomputed, "
        f"root {folded} == pinned"
    )

    # Tamper negative: flip the last byte of entry 1's payload — the content
    # address MUST diverge (that is the content-addressing law biting). The
    # untampered path above already restored the original payload, so a
    # divergence here plus PASS above is the restore-to-green pair.
    s1 = kat_entries[0]
    tampered = bytearray(payloads[s1])
    tampered[-1] = tampered[-1] ^ 0x01
    if hashlib.sha256(bytes(tampered)).digest() == recomputed[s1]:
        print("REFUSED: tamper negative failed — one-byte flip did NOT diverge the address")
        return 1
    print(
        f"PASS content-address-kat-tamper: one-byte flip of {s1} diverged "
        f"(untampered recomputation above restored the pinned root, exit 0 path)"
    )

    violations = 0
    for gate in sorted((PACK_DIR / "gates").glob("*.rq")):
        query = gate.read_text(encoding="utf-8")
        # rdflib types Result.__iter__ as Iterator[Union[_TripleType, bool,
        # ResultRow]]; SELECT rows are always iterable tuples, so narrow via cast.
        rows = list(cast(Iterable[tuple], graph.query(query)))
        if rows:
            violations += 1
            print(f"VIOLATION {gate.name}: {len(rows)} row(s)")
            for row in rows:
                print("  " + "; ".join(str(c) for c in row))
        else:
            print(f"PASS {gate.name}: 0 rows")

    if violations:
        print(f"FAIL: {violations} gate(s) with violations")
        return 1
    print("OK: all gates zero-rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
