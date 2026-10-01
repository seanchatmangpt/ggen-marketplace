"""graphlaw-wasm specimen for packs/wasi-json-abi-pack (graphlaw v26.9.29).

Chicago style: the real consumer graphs are rendered by the real ggen binary in a scratch copy, and
the committed generated/graphlaw/ projection is compared byte-for-byte with that render. Facts that
graphlaw itself owns (14 ops, limits, registry digests) are asserted against ~/graphlaw at the pinned
release SHA (git show; the dirty working tree is not the subject); the import list is asserted against the pack's own graph.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
from rdflib import Graph, Namespace

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "wasi-json-abi-pack"
GENERATED = PACK / "generated" / "graphlaw"
GRAPHLAW = Path.home() / "graphlaw"
GRAPHLAW_SHA = "0bb0df2a93293af5447bbe22f2a38eb645204f4c"  # graphlaw v26.9.29 release merge
WJA = Namespace("https://ggen.dev/ontology/wasi-json-abi#")
WASI_IMPORTS = {
    "random_get", "environ_get", "environ_sizes_get", "clock_time_get",
    "fd_write", "proc_exit", "sched_yield",
}
OPS = ["capabilities", "sniff", "parse", "convert", "canonical", "sparql", "shacl", "shex",
       "n3", "entail", "datalog", "hooks", "law", "policy"]


def merged() -> Graph:
    g = Graph()
    for f in ("qualification/graphlaw-consumer.ttl", "qualification/graphlaw-ops.ttl", "ontology.ttl"):
        g.parse(PACK / f, format="turtle")
    return g


def test_fourteen_ops_in_order_with_fields_and_examples():
    g = merged()
    rows = list(g.query(
        """PREFIX wja: <https://ggen.dev/ontology/wasi-json-abi#>
        SELECT ?n ?o ?rq ?rs ?ex WHERE { ?op a wja:Op ; wja:opName ?n ; wja:opOrder ?o ;
          wja:requestFields ?rq ; wja:responseFields ?rs ; wja:exampleRequest ?ex } ORDER BY ?o"""))
    assert [str(r.n) for r in rows] == OPS
    assert [int(r.o) for r in rows] == list(range(1, 15))
    for r in rows:
        assert json.loads(str(r.ex))["op"] == str(r.n)


def test_seven_wasi_imports_all_in_snapshot_preview1():
    g = merged()
    got = {(str(m), str(n)) for m, n in g.query(
        """PREFIX wja: <https://ggen.dev/ontology/wasi-json-abi#>
        SELECT ?m ?n WHERE { ?i a wja:WasiImport ; wja:importModule ?m ; wja:importName ?n }""")}
    assert {n for _, n in got} == WASI_IMPORTS
    assert {m for m, _ in got} == {"wasi_snapshot_preview1"}


def graphlaw_blob(path: str) -> str | None:
    """Exact-SHA read from the graphlaw checkout; the working tree is not the subject."""
    proc = subprocess.run(["git", "-C", str(GRAPHLAW), "show", f"{GRAPHLAW_SHA}:{path}"],
                          capture_output=True, text=True)
    return proc.stdout if proc.returncode == 0 else None


def test_facts_match_graphlaw_registry_and_pins():
    reg_text = graphlaw_blob("registry/capability-registry.json")
    pin_text = graphlaw_blob("registry/ARTIFACTS.sha256")
    if reg_text is None or pin_text is None:
        pytest.skip(f"graphlaw {GRAPHLAW_SHA[:9]} not available in ~/graphlaw")
    reg = json.loads(reg_text)
    assert reg["graphlaw_version"] == "26.9.29"
    assert [o["name"] for o in reg["ops"]] == OPS
    g = merged()
    mod = next(g.subjects(WJA.crateName, None))
    assert int(g.value(mod, WJA.maxRequestBytes)) == reg["limits"]["max_request_bytes"]
    assert int(g.value(mod, WJA.maxJsonDepth)) == reg["limits"]["max_json_depth"]
    pins = {}
    for line in pin_text.splitlines():
        if line and not line.startswith("#"):
            kind, digest, size, _ = line.split()
            pins[kind] = (digest.removeprefix("sha256:"), size)
    assert str(g.value(mod, WJA.wasmSha256)) == pins["wasm"][0]
    assert str(int(g.value(mod, WJA.wasmBytes))) == pins["wasm"][1]
    assert str(g.value(mod, WJA.registrySha256)) == pins["registry"][0]
    assert str(g.value(mod, WJA.surfaceSha256)) == pins["surface"][0]


@pytest.mark.skipif(shutil.which("ggen") is None, reason="ggen binary absent")
def test_committed_projection_equals_fresh_render(tmp_path):
    scratch = tmp_path / "pack"
    shutil.copytree(PACK, scratch, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(scratch / "ggen-graphlaw.toml", scratch / "ggen.toml")
    proc = subprocess.run(["ggen", "sync", "run"], cwd=scratch, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr[-2000:]
    fresh = scratch / "generated" / "graphlaw"
    names = sorted(p.name for p in fresh.iterdir())
    assert names == sorted(p.name for p in GENERATED.iterdir())
    for name in names:
        assert (fresh / name).read_bytes() == (GENERATED / name).read_bytes(), name
    assert "ffi.rs" not in names
