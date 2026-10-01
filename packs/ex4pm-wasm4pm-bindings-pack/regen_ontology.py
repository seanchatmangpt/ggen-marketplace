#!/usr/bin/env python3
"""Deterministically re-embed the wasm4pm-ex4pm-bindings crate into ontology.ttl.

The crate (src/*.rs + Cargo.toml) is the source of truth; the pack's embedded
epm:sourceText / epm:manifestText blobs and the Phase-4 epm:AlgorithmBinding
individuals are projections of it.  This script never hand-edits a blob: every
blob is the crate file's bytes, escaped for a Turtle long string
(backslash first, then any run of >=3 double quotes, then leading/trailing
quote), and is verified by an rdflib round-trip (parsed literal == file bytes).

Usage:
  regen_ontology.py [--crate DIR] [--ontology FILE] [--check]

--check re-derives the expected ontology text and exits 1 if the file on disk
differs (no write).  Idempotent: running twice yields identical bytes.
"""
import argparse
import os
import re
import sys

EPM = "http://seanchatmangpt.github.io/packs/ex4pm-wasm4pm-bindings#"
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CRATE = os.environ.get(
    "EX4PM_BINDINGS_CRATE", "/Users/sac/wasm4pm/crates/wasm4pm-ex4pm-bindings"
)

# subject -> (class, property, crate-relative file, rdfs:comment)
BLOBS = [
    ("LibModule", "Module", "sourceText", "src/lib.rs",
     'wasm4pm-ex4pm-bindings lib.rs: shared buffer ABI (version_v1, alloc_v1, dealloc_v1, free_v1), '
     'the Phase-1 extern "C" exports (discover, conform, simulate, optimize, powl_mine) each paired '
     'with a <algo>_replay_v1 export mirroring wasm4pm-cmca\'s cmcaReplay convention, the mod '
     'declarations for phase2/phase2_playout/phase4_stats/prolog, and the alloc/dealloc roundtrip test.'),
    ("CargoManifest", "Manifest", "manifestText", "Cargo.toml",
     'wasm4pm-ex4pm-bindings Cargo.toml (version 26.8.27, publish = false): cdylib+rlib crate-type, '
     'serde/serde_json JSON request/response encoding, miniml/ocpq/wasm4pm-cognition/prolog8 path '
     'dependencies, the wasm4pm path dependency with features = ["hand_rolled_stats"], and the '
     'unsafe_code=allow lint override for the FFI boundary.'),
    ("Phase2Module", "Module", "sourceText", "src/phase2.rs",
     'wasm4pm-ex4pm-bindings phase2.rs: thin extern "C" wrappers over already-implemented '
     'wasm4pm-workspace algorithms (miniml survival/markov/bayesian, ocpq ocpq_eval_json, '
     'wasm4pm-cognition strips_plan/htn_plan/ctl_check/allen_temporal), reusing lib.rs ABI helpers.'),
    ("PlayoutModule", "Module", "sourceText", "src/phase2_playout.rs",
     'wasm4pm-ex4pm-bindings phase2_playout.rs: the playout export pair over the wasm4pm crate '
     '(petri_net + PlayoutConfig JSON in, PlayoutResult JSON out).'),
    ("PrologModule", "Module", "sourceText", "src/prolog.rs",
     'wasm4pm-ex4pm-bindings prolog.rs: the prolog_query export pair over the prolog8 crate '
     '(predicates/facts/rules/query JSON in, answered|denied|invalid result JSON out).'),
    ("Phase4StatsModule", "Module", "sourceText", "src/phase4_stats.rs",
     'wasm4pm-ex4pm-bindings phase4_stats.rs: 14 thin extern "C" wrappers (ks_statistic, '
     'ks_critical_value, regression, forecast, holt_forecast, ewma, trend_classify, mean, '
     'dot_product, euclidean_distance, standardize, median, percentile, std_deviation) over plain '
     'wasm4pm::{ml,hand_stats,prediction_drift} functions, each paired with a <algo>_replay_v1 export.'),
]

ALGO_CLASS_COMMENT = (
    "One ex4pm algorithm bound to a wasm4pm_ex4pm_bindings extern C export pair "
    "(<id>_v1, <id>_replay_v1). Phase-1/2/3 rows bind the native-Elixir-engine algorithms; "
    "Phase-4 rows (14 statistics/ML primitives from phase4_stats.rs) bind the "
    "Ex4pmEngine.Wasm.<Name> adapter modules directly. 33 bindings = 66 algorithm exports; "
    "the crate additionally exports 4 infra symbols (version/alloc/dealloc/free)."
)

# Phase-4 binding shapes (observed from the request/result structs in phase4_stats.rs).
# Export names and ids are derived mechanically from the export_name attributes;
# only the human-readable shapes live here, and the id set is asserted equal to
# the crate's phase4 export-id set.
P4_SHAPES = {
    "ks_statistic": ("sample_a: list(f64), sample_b: list(f64)", "ks_statistic: f64"),
    "ks_critical_value": ("n: usize, m: usize, alpha: f64", "ks_critical_value: f64"),
    "regression": ("x: list(f64), y: list(f64)",
                   "slope, intercept, r_squared, mae, rmse, residual_std: f64"),
    "forecast": ("data: list(f64), alpha: f64", "rmse, mae, mape, next_window: f64"),
    "holt_forecast": ("series: list(f64), alpha: f64, beta: f64",
                      "rmse, mae, mape, next_window: f64"),
    "ewma": ("values: list(f64), alpha: f64", "ewma: list(f64)"),
    "trend_classify": ("smoothed: list(f64)", "trend: string (rising|falling|stable)"),
    "mean": ("data: list(f64)", "mean: f64"),
    "dot_product": ("a: list(f64), b: list(f64)", "dot_product: f64"),
    "euclidean_distance": ("a: list(f64), b: list(f64)", "euclidean_distance: f64"),
    "standardize": ("data: list(list(f64))", "standardized: list(list(f64))"),
    "median": ("data: list(f64)", "median: f64|null"),
    "percentile": ("data: list(f64), p: f64", "percentile: f64|null"),
    "std_deviation": ("data: list(f64)", "std_deviation: f64|null"),
}

EXPORT_RE = re.compile(r'export_name\s*=\s*"([^"]+)"')


def camel(i):
    return "".join(p.capitalize() for p in i.split("_"))


def long_lit(s):
    """Escape s for a Turtle \"\"\"long string\"\"\" body (no delimiters)."""
    if "\r" in s:
        raise SystemExit("refusing: CR in source (Turtle long-string CR handling is lossy)")
    s = s.replace("\\", "\\\\")
    out, run = [], 0
    for ch in s:
        if ch == '"':
            run += 1
            if run >= 3:
                out.append('\\"')
                run = 0
                continue
        else:
            run = 0
        out.append(ch)
    t = "".join(out)
    if t.startswith('"'):
        t = '\\"' + t[1:]
    if t.endswith('"') and not t.endswith('\\"'):
        t = t[:-1] + '\\"'
    return t


def short_lit(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def read(crate, rel):
    with open(os.path.join(crate, rel), encoding="utf-8", newline="") as f:
        return f.read()


def blob_block(name, cls, prop, rel, comment, crate):
    return (f"epm:{name} a epm:{cls} ;\n    rdfs:comment {short_lit(comment)} ;\n"
            f'    epm:{prop} """{long_lit(read(crate, rel))}""" .\n')


def binding_block(i, crate_exports):
    n = camel(i)
    exp, rep = f"wasm4pm_ex4pm_{i}_v1", f"wasm4pm_ex4pm_{i}_replay_v1"
    assert exp in crate_exports and rep in crate_exports, i
    req, res = P4_SHAPES[i]
    return (f"epm:{n} a epm:AlgorithmBinding ;\n"
            f'    epm:algorithmId "{i}" ;\n'
            f'    epm:elixirModuleName "{n}" ;\n'
            f'    epm:elixirSourceModule "Ex4pmEngine.Wasm.{n}" ;\n'
            f'    epm:wasmExportName "{exp}" ;\n'
            f'    epm:wasmReplayExportName "{rep}" ;\n'
            f'    epm:requestShape {short_lit(req)} ;\n'
            f'    epm:resultShape {short_lit(res)} ;\n'
            f'    epm:bcinrLike false ;\n'
            f'    epm:wasm4pmSourceCrate "wasm4pm" .\n')


def crate_export_names(crate, rel):
    return EXPORT_RE.findall(read(crate, rel))


def derive(text, crate):
    # 1. blobs
    for name, cls, prop, rel, comment in BLOBS:
        block = blob_block(name, cls, prop, rel, comment, crate)
        pat = re.compile(
            rf'^epm:{name} a epm:\w+ ;\n    rdfs:comment "(?:[^"\\]|\\.)*" ;\n'
            rf'    epm:{prop} """.*?\n""" \.\n', re.S | re.M)
        if pat.search(text):
            text = pat.sub(lambda m: block, text, count=1)
        else:
            anchor = "epm:AlgorithmBinding a rdfs:Class"
            assert anchor in text
            text = text.replace(anchor, block + "\n" + anchor, 1)
    # 2. class comment
    text, n = re.subn(
        r'(^epm:AlgorithmBinding a rdfs:Class ;\n    rdfs:comment )"(?:[^"\\]|\\.)*"( \.)',
        lambda m: m.group(1) + short_lit(ALGO_CLASS_COMMENT) + m.group(2),
        text, count=1, flags=re.M)
    assert n == 1, "AlgorithmBinding class comment not found"
    # 3. phase-4 bindings
    p4 = crate_export_names(crate, "src/phase4_stats.rs")
    ids = sorted({re.fullmatch(r"wasm4pm_ex4pm_(.+?)(?:_replay)?_v1", e).group(1) for e in p4})
    assert set(ids) == set(P4_SHAPES), (sorted(set(ids) ^ set(P4_SHAPES)))
    allexp = set(p4)
    for i in sorted(P4_SHAPES):
        block = binding_block(i, allexp)
        n = camel(i)
        pat = re.compile(rf'^epm:{n} a epm:AlgorithmBinding ;\n(?:    [^\n]*\n)+', re.M)
        if pat.search(text):
            text = pat.sub(lambda m: block, text, count=1)
        else:
            text = text.rstrip("\n") + "\n\n" + block
    return text


def verify_roundtrip(path, crate):
    import rdflib
    g = rdflib.Graph()
    g.parse(path, format="turtle")
    ok = True
    for name, _cls, prop, rel, _c in BLOBS:
        v = g.value(rdflib.URIRef(EPM + name), rdflib.URIRef(EPM + prop))
        same = v is not None and str(v) == read(crate, rel)
        print(f"roundtrip {name:18s} {rel:24s} {'BYTE-EQUAL' if same else 'MISMATCH'}")
        ok &= same
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crate", default=DEFAULT_CRATE)
    ap.add_argument("--ontology", default=os.path.join(HERE, "ontology.ttl"))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    with open(a.ontology, encoding="utf-8", newline="") as f:
        cur = f.read()
    new = derive(cur, a.crate)
    if a.check:
        print("ontology up to date" if new == cur else "ontology DRIFTED from crate")
        return 0 if new == cur else 1
    if new != cur:
        with open(a.ontology, "w", encoding="utf-8", newline="") as f:
            f.write(new)
        print("ontology rewritten")
    else:
        print("ontology unchanged")
    return 0 if verify_roundtrip(a.ontology, a.crate) else 1


if __name__ == "__main__":
    sys.exit(main())
