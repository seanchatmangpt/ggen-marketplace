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

    # Witnessed-ledger-replay court (lane L27, L9-pattern extension): re-apply
    # the witnessed canonical apply_transition sequence through a faithful
    # Python port of the generated ledger law (generated/ledger_state.rs
    # LedgerState::apply_transition + recompute_root) and assert equality with
    # the pinned genesis root and chain head. Roots were derived by executing
    # the generated Rust law, not invented. Refuses on any divergence;
    # `--tamper` perturbs one witnessed amount to prove the court is
    # non-vacuous (REFUSED, exit 1).
    MASK64 = (1 << 64) - 1
    FNV_OFFSET = 0xCBF29CE484222325
    FNV_PRIME = 0x100000001B3

    def _fold(h: int, bs) -> int:
        for b in bs:
            h = ((h ^ b) * FNV_PRIME) & MASK64
        return h

    def _root(accounts: dict, index: int) -> bytes:
        h = FNV_OFFSET
        for aid in sorted(accounts):
            h = _fold(h, aid)
            bal = accounts[aid]
            h = _fold(h, [(bal >> (8 * k)) & 0xFF for k in range(16)])
        h = _fold(h, [(index >> (8 * k)) & 0xFF for k in range(8)])
        return bytes((h >> ((i % 8) * 8)) & 0xFF for i in range(32))

    GENESIS_ROOT = "143eb3db4a3dd71e143eb3db4a3dd71e143eb3db4a3dd71e143eb3db4a3dd71e"
    LEDGER_HEAD = "18b128727f1ad46318b128727f1ad46318b128727f1ad46318b128727f1ad463"

    accounts: dict = {}
    nonce_map: dict = {}
    for s, p, o in witness:
        pred = str(p)
        if pred.endswith("#balance"):
            acct = next(
                (
                    bytes.fromhex(str(v)[2:])
                    for ss, pp, v in witness.triples((s, None, None))
                    if str(pp).endswith("#account")
                ),
                None,
            )
            if acct is not None:
                accounts[acct] = int(str(o))
        elif pred.endswith("#nonce"):
            nonce_map[s] = int(str(o))

    txs: list = []
    for s, nonce in nonce_map.items():
        inputs: list = []
        outputs: list = []
        digest = None
        for ss, pp, o in witness.triples((s, None, None)):
            pred = str(pp)
            if pred.endswith("#input"):
                acct_hex, amt = str(o).split(":")
                inputs.append((bytes.fromhex(acct_hex[2:]), int(amt)))
            elif pred.endswith("#output"):
                acct_hex, amt = str(o).split(":")
                outputs.append((bytes.fromhex(acct_hex[2:]), int(amt)))
            elif pred.endswith("#digest"):
                digest = bytes.fromhex(str(o)[2:])
        if digest is not None:
            txs.append((nonce, inputs, outputs, digest))
    txs.sort(key=lambda t: t[0])

    genesis_root_w = next(
        (str(o) for s, p, o in witness if str(p).endswith("#genesisRoot")), None
    )
    head_w = next(
        (str(o) for s, p, o in witness if str(p).endswith("#ledgerHead")), None
    )

    if not txs or genesis_root_w is None or head_w is None:
        print("REFUSED: witnessed-ledger-replay witnesses missing")
        return 1
    if genesis_root_w.lower() != GENESIS_ROOT or head_w.lower() != LEDGER_HEAD:
        print(
            f"REFUSED: witnessed ledger root drift (witness genesis={genesis_root_w} "
            f"head={head_w} court genesis={GENESIS_ROOT} head={LEDGER_HEAD})"
        )
        return 1

    tamper = "--tamper" in sys.argv
    if tamper:
        # Tamper negative: perturb one witnessed input amount by +1 so that
        # sum(inputs) != sum(outputs) — the conservation valve must refuse.
        n, ins, outs, d = txs[0]
        txs[0] = (n, [(a, v + 1) for a, v in ins], outs, d)

    balances = dict(accounts)
    nonces: dict = {}
    seen: set = set()
    index = 0
    prev_root = _root(balances, 0)
    if prev_root.hex() != GENESIS_ROOT:
        print(
            f"REFUSED: genesis divergence (computed={prev_root.hex()} "
            f"pinned={GENESIS_ROOT})"
        )
        return 1
    for nonce, ins, outs, dg in txs:
        # Gate 1: replay valve (seen digest).
        if dg in seen:
            print(f"REFUSED: replay of digest {dg.hex()} at index {index + 1}")
            return 1
        # Gate 2: double-spend valve (strictly advancing nonces).
        for aid, _ in ins:
            if nonce == 0 or nonce <= nonces.get(aid, 0):
                print(f"REFUSED: double-spend (nonce {nonce}) at index {index + 1}")
                return 1
        # Gate 3: conservation.
        sum_in = sum(v for _, v in ins)
        sum_out = sum(v for _, v in outs)
        if sum_in != sum_out:
            print(
                f"REFUSED: conservation divergence at index {index + 1} "
                f"(in={sum_in} out={sum_out})"
            )
            return 1
        # Gate 4: masked funds check + commit.
        shadow = dict(balances)
        for aid, amt in ins:
            if shadow.get(aid, 0) < amt:
                print(f"REFUSED: insufficient funds at index {index + 1}")
                return 1
            shadow[aid] = shadow.get(aid, 0) - amt
        for aid, amt in outs:
            shadow[aid] = shadow.get(aid, balances.get(aid, 0)) + amt
        for aid, bal in shadow.items():
            if bal == 0 and not any(oa == aid for oa, _ in outs):
                balances.pop(aid, None)
            else:
                balances[aid] = bal
        for aid, _ in ins:
            nonces[aid] = nonce
        seen.add(dg)
        index += 1
        prev_root = _root(balances, index)

    if prev_root.hex() != LEDGER_HEAD:
        if tamper:
            print(
                "TAMPER NEGATIVE CONFIRMED: mutated witnessed amount refused "
                "(exit 1); court is non-vacuous. Restore = run without --tamper."
            )
        else:
            print(
                f"REFUSED: witnessed-ledger-replay divergence (computed={prev_root.hex()} "
                f"pinned={LEDGER_HEAD})"
            )
        return 1
    if tamper:
        print(
            "REFUSED: tamper run reached the pinned head — court failed to "
            "detect the mutated witnessed amount (vacuous court)"
        )
        return 1
    print(
        f"PASS witnessed-ledger-replay: recomputed head {prev_root.hex()} == pinned "
        f"over {len(txs)} transitions, genesis {GENESIS_ROOT[:16]}..., conservation exact"
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
