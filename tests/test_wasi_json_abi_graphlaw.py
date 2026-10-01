"""graphlaw-wasm specimen for packs/wasi-json-abi-pack (graphlaw v26.9.29).

Chicago style: the real consumer graphs are rendered by the real ggen binary in a scratch copy, and
the committed generated/graphlaw/ projection (including the ffi.rs shell) is compared byte-for-byte with
that render, and the generated shell is built for wasm32-wasip1 and run against graphlaw's own wasm_abi
suite next to the hand-written lib.rs (differential). Facts that
graphlaw itself owns (14 ops, limits, registry digests) are asserted against ~/graphlaw at the pinned
release SHA (git show; the dirty working tree is not the subject); the import list is asserted against the pack's own graph.
"""

from __future__ import annotations

import io
import json
import os
import re
import shutil
import subprocess
import tarfile
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
    assert "ffi.rs" in names


def test_graphlaw_contract_carries_allocation_discipline_facts():
    g = merged()
    mod = next(g.subjects(WJA.crateName, None))
    assert int(g.value(mod, WJA.maxOutstandingBytes)) == 256 * 1024 * 1024
    assert str(g.value(mod, WJA.bufferStyle)) == "vec"
    assert str(g.value(mod, WJA.abiModulePath)) == "graphlaw::abi"
    assert g.value(mod, WJA.hasAbiVersionExport).toPython() is False


def test_generated_shell_exports_no_abi_version_and_caps_outstanding_bytes():
    ffi = (GENERATED / "ffi.rs").read_text()
    assert "gl_abi_version" not in ffi
    assert "pub extern \"C\" fn gl_alloc" in ffi
    assert "MAX_OUTSTANDING_BYTES" in ffi and "Vec::from_raw_parts" in ffi
    meta = (GENERATED / "abi_meta.rs").read_text()
    assert "pub const MAX_OUTSTANDING_BYTES: usize = 268435456;" in meta


# --- differential: generated ffi.rs vs graphlaw's hand-written wasm/src/lib.rs -----------------

GLUE_LIB_RS = "//! Differential glue: module wiring for the generated ffi shell (declarations only).\nmod abi_meta;\nmod ffi;\n"


def _blocked(reason: str):
    pytest.skip("BLOCKED: " + reason)


def _wasm_exports(wasm: bytes) -> set[str]:
    """Names in the export section of a wasm binary (minimal LEB128 section walk)."""
    def leb(buf: bytes, i: int) -> tuple[int, int]:
        out = shift = 0
        while True:
            b = buf[i]
            i += 1
            out |= (b & 0x7F) << shift
            if not b & 0x80:
                return out, i
            shift += 7

    assert wasm[:4] == b"\0asm"
    i = 8
    while i < len(wasm):
        sec_id = wasm[i]
        size, i = leb(wasm, i + 1)
        if sec_id == 7:
            count, j = leb(wasm, i)
            names = set()
            for _ in range(count):
                n, j = leb(wasm, j)
                names.add(wasm[j:j + n].decode())
                j += n + 1
                _, j = leb(wasm, j)
            return names
        i += size
    raise AssertionError("no export section")


def _cargo(args, cwd, env_extra=None, timeout=1800):
    env = {**os.environ, "RUSTUP_AUTO_INSTALL": "0", **(env_extra or {})}
    return subprocess.run(["cargo", *args], cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)


@pytest.mark.skipif(shutil.which("ggen") is None, reason="BLOCKED: ggen binary absent")
def test_generated_ffi_matches_handwritten_lib_on_graphlaw_wasm_abi_suite(tmp_path):
    for tool in ("cargo", "rustup", "git"):
        if shutil.which(tool) is None:
            _blocked(f"{tool} not on PATH")
    tree = tmp_path / "gl"
    tree.mkdir()
    archive = subprocess.run(["git", "-C", str(GRAPHLAW), "archive", GRAPHLAW_SHA], capture_output=True)
    if archive.returncode != 0:
        _blocked(f"graphlaw {GRAPHLAW_SHA[:9]} not available in {GRAPHLAW} (git archive rc={archive.returncode})")
    tarfile.open(fileobj=io.BytesIO(archive.stdout)).extractall(tree, filter="data")
    # The toolchain pinned by graphlaw's rust-toolchain.toml must provide the wasm target.
    targets = subprocess.run(["rustup", "target", "list", "--installed"], cwd=tree,
                             env={**os.environ, "RUSTUP_AUTO_INSTALL": "0"}, capture_output=True, text=True)
    if targets.returncode != 0 or "wasm32-wasip1" not in targets.stdout.split():
        _blocked("wasm32-wasip1 not installed for the toolchain pinned in graphlaw/rust-toolchain.toml "
                 f"(rustup rc={targets.returncode}, installed={targets.stdout.split()}, "
                 f"stderr={targets.stderr.strip()[-200:]})")

    hand_lib = (tree / "wasm/src/lib.rs").read_text()
    assert "OUTSTANDING" in hand_lib and "gl_abi_version" not in hand_lib  # the subject being replaced
    target_dir = tmp_path / "target"
    build = ["build", "--offline", "-p", "graphlaw-wasm", "--target", "wasm32-wasip1", "--profile", "wasm",
             "--target-dir", str(target_dir)]
    built = target_dir / "wasm32-wasip1/wasm/graphlaw_wasm.wasm"

    proc = _cargo(build, tree)
    assert proc.returncode == 0, proc.stderr[-2000:]
    hand_wasm = tmp_path / "hand.wasm"
    shutil.copy(built, hand_wasm)

    scratch = tmp_path / "pack"
    shutil.copytree(PACK, scratch, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(scratch / "ggen-graphlaw.toml", scratch / "ggen.toml")
    rendered = subprocess.run(["ggen", "sync", "run"], cwd=scratch, capture_output=True, text=True)
    assert rendered.returncode == 0, rendered.stderr[-2000:]
    for name in ("ffi.rs", "abi_meta.rs"):
        fresh = (scratch / "generated" / "graphlaw" / name).read_bytes()
        assert fresh == (GENERATED / name).read_bytes(), name
        (tree / "wasm/src" / name).write_bytes(fresh)
    (tree / "wasm/src/lib.rs").write_text(GLUE_LIB_RS)

    proc = _cargo(build, tree)
    assert proc.returncode == 0, proc.stderr[-2000:]
    gen_wasm = tmp_path / "gen.wasm"
    shutil.copy(built, gen_wasm)

    # Same export surface: the three gl_* functions plus memory; no gl_abi_version in either.
    hand_exports, gen_exports = _wasm_exports(hand_wasm.read_bytes()), _wasm_exports(gen_wasm.read_bytes())
    assert hand_exports == gen_exports
    assert {"gl_alloc", "gl_free", "gl_call", "memory"} <= gen_exports
    assert "gl_abi_version" not in gen_exports

    # Same behavior: graphlaw's own wasm_abi suite (real wasmi runtime) against each artifact.
    outcomes = {}
    for label, wasm in (("hand", hand_wasm), ("generated", gen_wasm)):
        run = _cargo(["test", "--offline", "-p", "graphlaw", "--features", "abi", "--test", "wasm_abi",
                      "--target-dir", str(tmp_path / "host-target")], tree, {"GRAPHLAW_WASM": str(wasm)})
        assert run.returncode == 0, f"{label}: {run.stdout[-2000:]}{run.stderr[-1000:]}"
        outcomes[label] = sorted(re.findall(r"^test (\S+) \.\.\. ok$", run.stdout, re.M))
    assert outcomes["hand"], "wasm_abi suite ran no tests"
    assert outcomes["hand"] == outcomes["generated"]
    assert "wasm_outstanding_allocation_cap_refuses_then_recovers_after_free" in outcomes["generated"]
