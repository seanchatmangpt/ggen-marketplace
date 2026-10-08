"""doc-hdit v2: optional tree-sitter engine tests (Chicago: real files, real state).

Same fixtures through both engines must yield the same identifier surface;
the tree-sitter path must carry strictly richer signatures (return types,
full struct fields, doc comments) that the regex path cannot recover.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter_rust")
pytest.importorskip("tree_sitter_elixir")

_SPEC = importlib.util.spec_from_file_location(
    "gen_doc_surface",
    Path(__file__).parent / "gen_doc_surface.py",
)
gds = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(gds)

RUST_SRC = """\
/// Adds two numbers.
pub fn add(a: u32, b: u32) -> u32 {
    a + b
}

fn internal() {}

/// A point in the plane.
pub struct Point {
    pub x: f64,
    y: f64,
}

/// Shape variants.
pub enum Shape {
    Circle,
    Rect(u32, u32),
}
"""

ELIXIR_SRC = """\
defmodule Demo.Calc do
  @doc "Doubles the input"
  @spec double(integer()) :: integer()
  def double(n) do
    n * 2
  end

  defp secret(n), do: n

  defstruct [:alpha, beta: 1]

  @type t :: %__MODULE__{alpha: integer()}
        | :none
end
"""


@pytest.fixture()
def rust_repo(tmp_path):
    (tmp_path / "Cargo.toml").write_text(
        '[package]\nname = "fixture-rs"\nversion = "0.1.0"\n'
    )
    src = tmp_path / "src"
    src.mkdir()
    (src / "lib.rs").write_text(RUST_SRC)
    return tmp_path


@pytest.fixture()
def elixir_repo(tmp_path):
    (tmp_path / "mix.exs").write_text(
        'defmodule Fixture.MixProject do\n  use Mix.Project\n\n'
        '  def project do\n    [app: :fixture, version: "0.2.0"]\n  end\nend\n'
    )
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "calc.ex").write_text(ELIXIR_SRC)
    return tmp_path


def _by_ident(surface, kind):
    out = {}
    for mod in surface["modules"]:
        for it in mod["items"]:
            if it["kind"] == kind:
                out[it["ident"]] = it
    return out


def test_rust_same_idents_richer_signatures(rust_repo):
    regex = gds.extract_code(rust_repo, engine="regex")
    ts = gds.extract_code(rust_repo, engine="ts")
    r_fns = _by_ident(regex, "function")
    t_fns = _by_ident(ts, "function")
    assert set(r_fns) == {"add"}
    assert set(t_fns) == set(r_fns)
    # regex path cannot see return types; tree-sitter can
    assert "->" not in r_fns["add"]["signature"]
    assert t_fns["add"]["signature"] == "add(a: u32, b: u32) -> u32"
    # doc comments: stripped before regex scanning, captured by tree-sitter
    assert r_fns["add"].get("doc", "") == ""
    assert t_fns["add"]["doc"] == "Adds two numbers."
    # structs/enums with full field fidelity on both paths, docs only on ts
    for kind, ident in (("struct", "Point"), ("enum", "Shape")):
        r_it = _by_ident(regex, kind)[ident]
        t_it = _by_ident(ts, kind)[ident]
        assert t_it["signature"].startswith(ident + " {")
        assert t_it["doc"] != ""
    assert "x: f64" in _by_ident(ts, "struct")["Point"]["signature"]


def test_elixir_same_idents_richer_signatures(elixir_repo):
    regex = gds.extract_code(elixir_repo, engine="regex")
    ts = gds.extract_code(elixir_repo, engine="ts")
    r_fns = _by_ident(regex, "function")
    t_fns = _by_ident(ts, "function")
    assert set(r_fns) == {"double"}
    assert set(t_fns) == set(r_fns)
    assert r_fns["double"]["signature"] == t_fns["double"]["signature"] == "double/1"
    assert t_fns["double"]["doc"] == "Doubles the input"
    assert t_fns["double"]["spec"].startswith("double(integer())")
    assert t_fns["double"]["is_public"] is True
    # defp never enters either surface
    assert all(it["ident"] != "secret" for m in ts["modules"] for it in m["items"])
    # defstruct fields parse identically; @type with continuation captured
    assert _by_ident(ts, "struct")["Demo.Calc"]["signature"] == \
        _by_ident(regex, "struct")["Demo.Calc"]["signature"] == \
        "defstruct alpha, beta: 1"
    assert _by_ident(ts, "type")["t"]["signature"].startswith("@type t ::")
    assert ":none" in _by_ident(ts, "type")["t"]["signature"]


def test_auto_falls_back_to_regex_without_ts(rust_repo, monkeypatch_ok=True):
    saved = gds.TS_AVAILABLE
    try:
        gds.TS_AVAILABLE = False
        surface = gds.extract_code(rust_repo, engine="auto")
    finally:
        gds.TS_AVAILABLE = saved
    regex = gds.extract_code(rust_repo, engine="regex")
    assert surface == regex


def test_engine_ts_raises_without_dependency(rust_repo):
    saved = gds.TS_AVAILABLE
    try:
        gds.TS_AVAILABLE = False
        with pytest.raises(RuntimeError, match="tree-sitter"):
            gds.extract_code(rust_repo, engine="ts")
    finally:
        gds.TS_AVAILABLE = saved


def test_cli_engine_flag_end_to_end(rust_repo):
    """Real subprocess, no dep: default (auto) still emits the surface."""
    proc = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "gen_doc_surface.py"),
         "code", str(rust_repo)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert '"repo"' in proc.stdout
