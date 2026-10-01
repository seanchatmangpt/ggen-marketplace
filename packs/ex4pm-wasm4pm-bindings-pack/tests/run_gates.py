#!/usr/bin/env python3
"""Executes every gate for real (python + rdflib SPARQL engine) and its negative control.

  - 010/030/040/050 (.rq) on the real ontology.ttl: must return 0 rows.
  - each .rq on its tests/fixtures/neg_*.ttl: must return exactly the expected rows.
  - 060 (python) on the real crate: exit 0; on a temp copy of the crate with one export
    renamed: exit 1 with BINDING_NOT_IN_CRATE + CRATE_EXPORT_UNBOUND + EMBED_HASH_MISMATCH.
Exit 0 iff every expectation holds.
"""
import os
import shutil
import subprocess
import sys
import tempfile

import rdflib

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)
CRATE = os.environ.get("EX4PM_BINDINGS_CRATE", "/Users/sac/wasm4pm/crates/wasm4pm-ex4pm-bindings")
EPM = "http://seanchatmangpt.github.io/packs/ex4pm-wasm4pm-bindings#"

GATES = ["010_required", "030_value_constraints", "040_required_abi", "050_binding_source_agreement"]
NEG = {  # gate -> (fixture, expected rows as tuples of str)
    "010_required": ("neg_010_missing_prop.ttl", {(EPM + "Bad", EPM + "resultShape")}),
    "030_value_constraints": ("neg_030_bad_prefix.ttl", {(EPM + "Bad", EPM + "wasmExportName", "other_bad_v1")}),
    "040_required_abi": ("neg_040_alloc_missing.ttl", {("wasm4pm_ex4pm_bindings_alloc_v1",)}),
    "050_binding_source_agreement": ("neg_050_unmatched_export.ttl",
                                     {(EPM + "A", EPM + "wasmReplayExportName", "wasm4pm_ex4pm_a_replay_v1")}),
}
fails = 0


def rows(gate, ttl):
    g = rdflib.Graph()
    g.parse(ttl, format="turtle")
    q = open(os.path.join(PACK, "gates", gate + ".rq")).read()
    return {tuple(str(c) for c in r) for r in g.query(q)}


def expect(label, ok, detail=""):
    global fails
    print(f"{'PASS' if ok else 'FAIL'}  {label} {detail}")
    fails += 0 if ok else 1


real = os.path.join(PACK, "ontology.ttl")
for gate in GATES:
    r = rows(gate, real)
    expect(f"{gate} on real ontology -> 0 rows", not r, f"(got {len(r)})")
    fx, want = NEG[gate]
    r = rows(gate, os.path.join(HERE, "fixtures", fx))
    expect(f"{gate} negative control {fx} fires exactly expected rows", r == want, f"(got {sorted(r)})")

g060 = os.path.join(PACK, "gates", "060_crate_drift.py")
p = subprocess.run([sys.executable, g060, "--crate", CRATE, "--ontology", real], capture_output=True, text=True)
expect("060 on real crate -> exit 0", p.returncode == 0, p.stdout.strip().splitlines()[-1:] and p.stdout.strip().splitlines()[-1])

with tempfile.TemporaryDirectory() as td:
    cp = os.path.join(td, "crate")
    shutil.copytree(CRATE, cp, ignore=shutil.ignore_patterns("target"))
    f = os.path.join(cp, "src", "phase4_stats.rs")
    s = open(f).read()
    assert '"wasm4pm_ex4pm_ks_statistic_v1"' in s
    open(f, "w").write(s.replace('"wasm4pm_ex4pm_ks_statistic_v1"', '"wasm4pm_ex4pm_ks_statistic_v2"'))
    p = subprocess.run([sys.executable, g060, "--crate", cp, "--ontology", real], capture_output=True, text=True)
    out = p.stdout
    expect("060 on mutated crate copy -> exit 1", p.returncode == 1)
    for code in ("BINDING_NOT_IN_CRATE\twasm4pm_ex4pm_ks_statistic_v1", "CRATE_EXPORT_UNBOUND\twasm4pm_ex4pm_ks_statistic_v2",
                 "REPLAY_PAIR_BROKEN", "EMBED_HASH_MISMATCH"):
        expect(f"060 mutated emits {code.split(chr(9))[0]}", code in out)
    print(out)

    # INFRA_MISSING control: drop alloc_v1 export attribute from a copy
    cp2 = os.path.join(td, "crate2")
    shutil.copytree(CRATE, cp2, ignore=shutil.ignore_patterns("target"))
    f = os.path.join(cp2, "src", "lib.rs")
    s = open(f).read()
    open(f, "w").write(s.replace('"wasm4pm_ex4pm_bindings_alloc_v1"', '"renamed_alloc"'))
    p = subprocess.run([sys.executable, g060, "--crate", cp2, "--ontology", real], capture_output=True, text=True)
    expect("060 infra-renamed copy emits INFRA_MISSING + exit 1", p.returncode == 1 and "INFRA_MISSING" in p.stdout)

print("RESULT", "ALL PASS" if not fails else f"{fails} FAILED")
sys.exit(1 if fails else 0)
