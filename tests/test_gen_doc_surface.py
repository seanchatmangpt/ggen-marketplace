"""P2 scope + external-allowlist extractor tests (DOC-HDIT-PILOT P2)."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import gen_doc_surface as g  # noqa: E402


def mkrepo(layout):
    repo = Path(tempfile.mkdtemp())
    for rel, text in layout.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return repo


class P2ExtractorTest(unittest.TestCase):
    def test_elixir_defp_and_doc_false_are_internal(self):
        src = (
            "defmodule Demo do\n"
            "  @doc false\n"
            "  def hidden(x), do: x\n"
            "  defp secret(y), do: y\n"
            "  def visible(z), do: z\n"
            "  def shown(w), do: w\n"
            "end\n"
        )
        repo = mkrepo({"mix.exs": "defmodule Demo.MixProject do\n  def project, do: []\nend\n", "lib/demo.ex": src})
        code = g.extract_code(repo)
        items = {
            it["ident"]: it
            for m in code["modules"]
            for it in m["items"]
            if it["kind"] == "function"
        }
        assert items["hidden"]["is_public"] is False
        assert items["secret"]["is_public"] is False
        assert items["visible"]["is_public"] is True
        assert items["shown"]["is_public"] is True

    def test_rust_internal_dirs_not_public(self):
        repo = mkrepo({
            "Cargo.toml": '[package]\nname = "demo"\nversion = "0.1.0"\n',
            "src/lib.rs": "pub fn ignite() {}\n",
            "tests/it.rs": "pub fn helper() {}\n",
        })
        code = g.extract_code(repo)
        mods = {m["name"]: m for m in code["modules"]}
        assert mods["src/lib.rs"]["is_public"] is True
        assert mods["tests/it.rs"]["is_public"] is False

    def test_rust_pub_items_flagged_public(self):
        repo = mkrepo({
            "Cargo.toml": '[package]\nname = "demo"\nversion = "0.1.0"\n',
            "src/lib.rs": "pub fn ignite() {}\n",
        })
        code = g.extract_code(repo)
        items = [it for m in code["modules"] for it in m["items"]]
        assert items and all(it["is_public"] is True for it in items)

    def test_known_external_elixir_and_rust_deps(self):
        repo = mkrepo({
            "mix.exs": (
                "defmodule Demo.MixProject do\n"
                "  def project do\n"
                "    [app: :demo, deps: deps()]\n"
                "  end\n"
                "  defp deps do\n"
                "    [\n"
                "      {:ash, \"~> 3.0\"},\n"
                "      {:ash_postgres, \"~> 2.0\"},\n"
                "      {:wasmex, \"~> 0.9\"}\n"
                "    ]\n"
                "  end\n"
                "end\n"
            ),
            "Cargo.toml": (
                '[package]\nname = "demo"\nversion = "0.1.0"\n\n'
                '[dependencies]\nserde_json = "1"\n'
            ),
        })
        ext = g.known_external(repo)
        assert "Ash." in ext
        assert "AshPostgres." in ext
        assert "Wasmex." in ext
        assert "serde_json::" in ext

    def test_extract_code_emits_known_external(self):
        repo = mkrepo({
            "Cargo.toml": (
                '[package]\nname = "demo"\nversion = "0.0.1"\n\n'
                '[dependencies]\nserde_json = "1"\n'
            ),
            "src/lib.rs": "pub fn ignite() {}\n",
        })
        code = g.extract_code(repo)
        assert isinstance(code["known_external"], list)
        assert "serde_json::" in code["known_external"]


class P3ProseFilterTest(unittest.TestCase):
    """P3: path/version/prose spans are not emitted as symbol claims."""

    def test_witnessed_path_and_version_spans_are_noise(self):
        assert g.is_noise_span("release/v26.8.23")
        assert g.is_noise_span("stream/metrics.ex")
        assert g.is_noise_span("stage/{id}.jsonl")
        assert g.is_noise_span("v26.8.23")
        assert g.is_noise_span("1.2.3")

    def test_symbol_arity_and_qualified_spans_survive(self):
        assert not g.is_noise_span("verify/0")
        assert not g.is_noise_span("Ex4pm.OCEL.normalize/1")
        assert not g.is_noise_span("s_coverage_set")

    def test_doc_mode_does_not_emit_prose_claims(self):
        repo = mkrepo({
            "mix.exs": "defmodule Demo.MixProject do\n  def project, do: []\nend\n",
            "lib/demo.ex": "defmodule Demo.Engine do\n  def ignite(x), do: x\nend\n",
            "docs/guide.md": (
                "Run the release pipeline.\n\n"
                "Use `Demo.Engine.ignite`, see `release/v26.8.23` and `stream/metrics.ex`.\n"
            ),
        })
        surface = g.extract_code(repo)
        claims = g.extract_doc(repo, surface)["claims"]
        objs = [c["object"] for c in claims]
        assert "release/v26.8.23" not in objs
        assert "stream/metrics.ex" not in objs
        assert "Demo.Engine.ignite" in objs


if __name__ == "__main__":
    unittest.main()
