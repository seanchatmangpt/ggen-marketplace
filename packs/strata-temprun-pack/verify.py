#!/usr/bin/env python3
"""Real Chicago verifier: re-run every gates/*.rq SELECT against ontology.ttl.
Exit 0 iff every gate returns zero rows (violation-free); else print and exit 1."""
import hashlib
import sys
from pathlib import Path

from typing import Iterable, cast

from rdflib import Graph, URIRef

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
    print("OK: all gates zero-rows")

    # KAT — replay the witnessed admission-fuel sieve sequence.
    kat_rc = replay_kat(witness)
    return kat_rc


def run_sieve(fuel: int, steps: int, holder: str) -> tuple[str, int, str]:
    """Python mirror of ActuationArena::run/2 (all-or-nothing 1-fuel steps)."""
    step = 0
    while step < steps:
        if fuel == 0:
            return (
                "REFUSE",
                0,
                f"fuel exhausted at step {step} of {steps} (lease held by {holder})",
            )
        fuel -= 1
        step += 1
    return "ADMIT", fuel, ""


def replay_kat(witness: Graph) -> int:
    SW = "https://strata.chatman.ai/ontology/witness#"
    KAT = URIRef("https://strata.chatman.ai/witness/strata-temprun-pack#kat-admission-fuel-3")

    types = {str(o) for o in witness.objects(KAT, None)}
    if f"{SW}KatRun" not in types:
        print("REFUSED: KAT witness node missing")
        return 1

    # Subject binding: pinned arena.rs hash must match the file on disk.
    subject = str(next(witness.objects(KAT, URIRef(f"{SW}subjectSha256"))))
    arena = PACK_DIR / "generated" / "arena.rs"
    actual = hashlib.sha256(arena.read_bytes()).hexdigest()
    if actual != subject:
        print(f"REFUSED: arena.rs hash drift (witness={subject[:12]} disk={actual[:12]})")
        return 1

    attempts = sorted(
        (a for a in witness.objects(KAT, URIRef(f"{SW}attempt"))),
        key=lambda a: int(str(next(witness.objects(a, URIRef(f"{SW}order"))))),
    )
    if not attempts:
        print("REFUSED: KAT has no pinned attempts")
        return 1

    results = []
    for a in attempts:
        get = lambda p: next(witness.objects(a, URIRef(f"{SW}{p}")))
        name = str(get("name"))
        fuel = int(str(get("requestFuel")))
        steps = int(str(get("steps")))
        pinned = {
            "outcome": str(get("outcome")),
            "finalFuel": int(str(get("finalFuel"))),
            "detail": str(witness.value(a, URIRef(f"{SW}detail"), default="")),
        }
        outcome, final_fuel, detail = run_sieve(fuel, steps, name)
        results.append((name, outcome, final_fuel))

        if outcome != pinned["outcome"] or final_fuel != pinned["finalFuel"]:
            print(
                f"REFUSED: KAT attempt {name} mismatch "
                f"(pinned={pinned['outcome']}/{pinned['finalFuel']} "
                f"replayed={outcome}/{final_fuel})"
            )
            return 1
        if outcome == "REFUSE" and detail != str(get("detail")):
            print(f"REFUSED: KAT attempt {name} detail drift")
            return 1
        print(f"KAT PASS {name}: {outcome} fuel={final_fuel}")

    pinned_final = int(str(next(witness.objects(KAT, URIRef(f"{SW}finalFuel")))))
    last_fuel = results[-1][2]
    if last_fuel != pinned_final:
        print(f"REFUSED: KAT final fuel drift (pinned={pinned_final} replayed={last_fuel})")
        return 1
    print(f"KAT PASS final_fuel={last_fuel}")

    # Tamper negative — flip attempt a1's pinned outcome to ADMIT; the replay
    # must refuse the corrupted witness, proving the KAT is non-vacuous.
    tampered = witness.serialize(format="turtle")
    bad = tampered.replace(
        'sw:outcome "REFUSE"', 'sw:outcome "ADMIT"', 1
    )
    if bad == tampered:
        print("NOTE: no REFUSE outcome pinned; tamper negative skipped")
        return 0
    bad_graph = Graph()
    bad_graph.parse(data=bad, format="turtle")
    probe = f"{SW}KatRun"
    # Replay the tampered sequence directly against the pinned expectations
    # copied from the tampered graph: the tampered a1 pins ADMIT but the real
    # sieve refuses — re-verifying through replay_kat on the tampered graph
    # must exit nonzero.
    rc_probe = replay_kat_probe(bad_graph)
    if rc_probe == 0:
        print("REFUSED: tamper negative not caught — KAT is vacuous")
        return 1
    print("KAT PASS tamper-negative: flipped outcome refused as expected")
    return 0


def replay_kat_probe(bad_graph: Graph) -> int:
    """Replay only the pinned-outcome vs sieve comparison on a tampered graph."""
    SW = "https://strata.chatman.ai/ontology/witness#"
    KAT = URIRef("https://strata.chatman.ai/witness/strata-temprun-pack#kat-admission-fuel-3")
    for a in bad_graph.objects(KAT, URIRef(f"{SW}attempt")):
        get = lambda p: next(bad_graph.objects(a, URIRef(f"{SW}{p}")))
        name = str(get("name"))
        outcome, final_fuel, _ = run_sieve(
            int(str(get("requestFuel"))), int(str(get("steps"))), name
        )
        if outcome != str(get("outcome")) or final_fuel != int(str(get("finalFuel"))):
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
