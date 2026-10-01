#!/usr/bin/env python3
"""060 crate-drift gate: pack ontology vs the live wasm4pm-ex4pm-bindings crate.

Typed findings (exit 1 if any):
  CRATE_EXPORT_UNBOUND  crate algorithm export with no epm:AlgorithmBinding
  BINDING_NOT_IN_CRATE  binding export name absent from crate src/*.rs
  INFRA_MISSING         one of the 4 infra exports absent from the crate
  REPLAY_PAIR_BROKEN    <id>_v1 without <id>_replay_v1 (or inverse), in crate or in bindings
  EMBED_HASH_MISMATCH   embedded sourceText/manifestText sha256 != crate file sha256
  COUNT_IDENTITY        2*bindings + 4 != distinct export_name attributes in the crate

Usage: 060_crate_drift.py [--crate DIR] [--ontology FILE]
"""
import argparse
import glob
import hashlib
import os
import re
import sys

EPM = "http://seanchatmangpt.github.io/packs/ex4pm-wasm4pm-bindings#"
HERE = os.path.dirname(os.path.abspath(__file__))
INFRA = {
    "wasm4pm_ex4pm_bindings_version_v1", "wasm4pm_ex4pm_bindings_alloc_v1",
    "wasm4pm_ex4pm_bindings_dealloc_v1", "wasm4pm_ex4pm_bindings_free_v1",
}
EMBEDS = [("LibModule", "sourceText", "src/lib.rs"), ("Phase2Module", "sourceText", "src/phase2.rs"),
          ("PlayoutModule", "sourceText", "src/phase2_playout.rs"),
          ("PrologModule", "sourceText", "src/prolog.rs"),
          ("Phase4StatsModule", "sourceText", "src/phase4_stats.rs"),
          ("CargoManifest", "manifestText", "Cargo.toml")]
EXPORT_RE = re.compile(r'export_name\s*=\s*"([^"]+)"')


def sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def check(crate, ontology):
    import rdflib
    g = rdflib.Graph()
    g.parse(ontology, format="turtle")
    E = lambda n: rdflib.URIRef(EPM + n)
    findings = []

    crate_exports = set()
    for f in sorted(glob.glob(os.path.join(crate, "src", "*.rs"))):
        crate_exports |= set(EXPORT_RE.findall(open(f, encoding="utf-8").read()))
    algo_crate = crate_exports - INFRA

    bound = set()
    for b in g.subjects(rdflib.RDF.type, E("AlgorithmBinding")):
        ex = g.value(b, E("wasmExportName"))
        rp = g.value(b, E("wasmReplayExportName"))
        ex, rp = (str(ex) if ex else None), (str(rp) if rp else None)
        for x in (ex, rp):
            if x:
                bound.add(x)
                if x not in crate_exports:
                    findings.append(("BINDING_NOT_IN_CRATE", x))
        if not (ex and rp and ex.endswith("_v1") and rp == ex[:-3] + "_replay_v1"):
            findings.append(("REPLAY_PAIR_BROKEN", f"binding {b}: {ex} / {rp}"))
    nbind = len(set(g.subjects(rdflib.RDF.type, E("AlgorithmBinding"))))

    for x in sorted(algo_crate - bound):
        findings.append(("CRATE_EXPORT_UNBOUND", x))
    for x in sorted(INFRA - crate_exports):
        findings.append(("INFRA_MISSING", x))
    for x in sorted(algo_crate):
        if x.endswith("_replay_v1"):
            base = x[: -len("_replay_v1")] + "_v1"
            if base not in crate_exports:
                findings.append(("REPLAY_PAIR_BROKEN", f"crate {x} has no {base}"))
        elif x.endswith("_v1"):
            rep = x[:-3] + "_replay_v1"
            if rep not in crate_exports:
                findings.append(("REPLAY_PAIR_BROKEN", f"crate {x} has no {rep}"))

    for name, prop, rel in EMBEDS:
        v = g.value(E(name), E(prop))
        disk = open(os.path.join(crate, rel), "rb").read()
        if v is None:
            findings.append(("EMBED_HASH_MISMATCH", f"{name}: no {prop} embedded"))
        elif str(v).encode("utf-8") != disk:
            findings.append(("EMBED_HASH_MISMATCH",
                             f"{name} {rel}: embedded {sha(str(v).encode())} != crate {sha(disk)}"))

    if 2 * nbind + len(INFRA) != len(crate_exports):
        findings.append(("COUNT_IDENTITY",
                         f"2*{nbind}+{len(INFRA)}={2*nbind+len(INFRA)} != {len(crate_exports)} crate exports"))
    return findings, nbind, len(crate_exports)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crate", default=os.environ.get(
        "EX4PM_BINDINGS_CRATE", "/Users/sac/wasm4pm/crates/wasm4pm-ex4pm-bindings"))
    ap.add_argument("--ontology", default=os.path.join(HERE, "..", "ontology.ttl"))
    a = ap.parse_args()
    findings, nb, ne = check(a.crate, a.ontology)
    for code, detail in findings:
        print(f"{code}\t{detail}")
    print(f"060 bindings={nb} crate_exports={ne} findings={len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
