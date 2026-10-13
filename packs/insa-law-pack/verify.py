#!/usr/bin/env python3
"""Real Chicago verifier for insa-law-pack: re-run every gates/*.rq SELECT
against ontology.ttl with rdflib. Exit 0 iff every gate returns zero rows
(violation-free); else print violations and exit 1.
Additionally proves the projected Rust vow_order table compiles and its gate
suite passes under the real toolchain (rustc --test), when rustc is available.
Finally, cross-checks the generated table's chain against the pinned insa
chain snapshot (pinned/insa_eight_vow_chain.txt)."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable, cast

from rdflib import Graph

PACK_DIR = Path(__file__).resolve().parent


def run_gates() -> int:
    graph = Graph()
    graph.parse(PACK_DIR / "ontology.ttl", format="turtle")

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
    return violations


def run_pinned_chain_check() -> bool:
    """Cross-check hook: generated chain must equal the pinned insa chain."""
    generated = PACK_DIR / "generated" / "vow_order.rs"
    pinned = PACK_DIR / "pinned" / "insa_eight_vow_chain.txt"
    if not generated.exists():
        print("NOTE: no generated/vow_order.rs; pinned chain check not run")
        return True
    expected = [
        line.split("#", 1)[0].strip()
        for line in pinned.read_text(encoding="utf-8").splitlines()
        if line.split("#", 1)[0].strip()
    ]
    import re
    text = generated.read_text(encoding="utf-8")
    projected = re.findall(
        r'ordinal:\s*(\d+),\s*from_state:\s*"([^"]+)",\s*to_state:\s*"([^"]+)",'
        r'\s*edge_fn:\s*"([^"]+)"',
        text,
    )
    ok = True
    if len(projected) != len(expected):
        print(f"VIOLATION pinned-chain: projected {len(projected)} rows, pinned {len(expected)}")
        ok = False
    for (po, pf, pt, pe), entry in zip(projected, expected):
        # pinned entry: "<ordinal> <from>-><to> <edge_fn>"
        ord_, chain, edge = entry.split(None, 2)
        f, t = chain.split("->")
        if (po, pf, pt, pe) != (ord_, f, t, edge):
            print(f"VIOLATION pinned-chain: projected ({po},{pf},{pt},{pe}) != pinned {entry}")
            ok = False
    if ok:
        print(f"PASS pinned-chain: {len(expected)} entries match generated table")
    return ok


def run_rust_suite() -> bool:
    generated = PACK_DIR / "generated" / "vow_order.rs"
    rustc = shutil.which("rustc")
    if not generated.exists():
        print("NOTE: no generated/vow_order.rs; rust gate suite not run")
        return True
    if rustc is None:
        print("NOTE: rustc not on PATH; rust gate suite not run")
        return True
    with tempfile.TemporaryDirectory() as td:
        bin_path = Path(td) / "vow_order_test"
        compile_result = subprocess.run(
            [rustc, "--test", str(generated), "-o", str(bin_path)],
            capture_output=True, text=True,
        )
        if compile_result.returncode != 0:
            print("VIOLATION rust-compile: generated/vow_order.rs failed to compile")
            print(compile_result.stderr)
            return False
        test_result = subprocess.run(
            [str(bin_path)], capture_output=True, text=True
        )
        if test_result.returncode != 0:
            print("VIOLATION rust-test: gate suite failed")
            print(test_result.stdout)
            print(test_result.stderr)
            return False
        passing = [line for line in test_result.stdout.splitlines() if "test result: ok" in line]
        print(f"PASS rust-gate-suite: {passing[0].strip() if passing else 'ok'}")
        return True


def main() -> int:
    violations = run_gates()
    if violations:
        print(f"FAIL: {violations} violation row(s)")
        return 1
    print("OK: all gates zero-rows")
    if not run_pinned_chain_check():
        return 1
    if not run_rust_suite():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
