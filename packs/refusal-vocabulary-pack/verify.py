#!/usr/bin/env python3
"""Real Chicago verifier: re-run every gates/*.rq SELECT against ontology.ttl.
Exit 0 iff every gate returns zero rows (violation-free); else print and exit 1.
Additionally proves the projected Rust crosswalk compiles and its gate suite
passes under the real toolchain (rustc --test), when rustc is available."""
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


def run_rust_suite() -> bool:
    generated = PACK_DIR / "generated" / "crosswalk.rs"
    rustc = shutil.which("rustc")
    if not generated.exists():
        print("NOTE: no generated/crosswalk.rs; rust gate suite not run")
        return True
    if rustc is None:
        print("NOTE: rustc not on PATH; rust gate suite not run")
        return True
    with tempfile.TemporaryDirectory() as td:
        bin_path = Path(td) / "crosswalk_test"
        compile_result = subprocess.run(
            [rustc, "--test", str(generated), "-o", str(bin_path)],
            capture_output=True, text=True,
        )
        if compile_result.returncode != 0:
            print("VIOLATION rust-compile: generated/crosswalk.rs failed to compile")
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
    if not run_rust_suite():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
