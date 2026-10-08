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


class P4TableClaimsTest(unittest.TestCase):
    """P4: markdown pipe-table rows emit symbol claims (scaffold tables count)."""

    def _surface_and_claims(self, docs_md):
        repo = mkrepo({
            "mix.exs": "defmodule Demo.MixProject do\n  def project, do: []\nend\n",
            "lib/demo.ex": (
                "defmodule Demo.Engine do\n"
                "  @doc false\n"
                "  def ignite(x, opts \\\\ []), do: {x, opts}\n"
                "  def execute(a, b, c, opts \\\\ []), do: {a, b, c, opts}\n"
                "end\n"
            ),
            "docs/reference.md": docs_md,
        })
        surface = g.extract_code(repo)
        return g.extract_doc(repo, surface)["claims"]

    def test_table_rows_emit_symbol_claims(self):
        md = (
            "| Function | Signature | Params | Default |\n"
            "|---|---|---|---|\n"
            "| `Demo.Engine.ignite/2` | `ignite(x, opts \\\\ [])` | `opts` | `[]` |\n"
            "| `Not.A.Real.symbol/9` | `bogus(a)` | `a` | `1` |\n"
        )
        claims = self._surface_and_claims(md)
        mentions = {(c["object"], c["kind"]) for c in claims if c["predicate"] == "mentions"}
        assert ("Demo.Engine.ignite/2", "table_row") in mentions, claims
        # fake symbol in a Function column is still a doc claim — the audit
        # gate must see it (phantom channel), extractor does not silently drop it
        assert ("Not.A.Real.symbol/9", "table_row_scaffold") in mentions, claims

    def test_table_has_param_claim_carries_identifier(self):
        md = (
            "| Function | Params | Default |\n"
            "|---|---|---|\n"
            "| `Demo.Engine.ignite/2` | `opts` | `[]` |\n"
        )
        claims = self._surface_and_claims(md)
        hp = [c for c in claims if c["predicate"] == "has_param"]
        assert len(hp) == 1, claims
        # the object is the identifier itself — a groundable code-surface
        # symbol string, not a whole-cell span and not a nested dict
        assert hp[0]["object"] == "Demo.Engine.ignite/2"
        assert hp[0]["kind"] == "param_table"

    def test_prose_cells_do_not_become_claims(self):
        md = (
            "| Function | Notes |\n"
            "|---|---|\n"
            "| `Demo.Engine.ignite/2` | see `release/v26.8.23` and the runbook |\n"
        )
        claims = self._surface_and_claims(md)
        objs = [c["object"] for c in claims if c["predicate"] == "mentions"]
        assert "release/v26.8.23" not in objs
        assert "runbook" not in objs
        assert "Demo.Engine.ignite/2" in objs

    def test_witnessed_ex4pm_offenders_resolved(self):
        """The two witnessed ex4pm phantom rows (DOC-HDIT-PILOT P3 audit:
        offending_claims=[880, 981]) must not re-appear as whole-span claims."""
        md = (
            "| Item | Purpose |\n"
            "|---|---|\n"
            "| `Demo.Engine.ignite/2` (`stream/ingest.ex:19`) | validated batch |\n"
        )
        claims = self._surface_and_claims(md)
        objs = [c["object"] for c in claims]
        assert "stream/ingest.ex:19" not in objs, claims
        md2 = "resolved: `execute/4,5` and `admit/2` confirmed real\n"
        claims2 = self._surface_and_claims(md2)
        objs2 = [c["object"] for c in claims2]
        assert "execute/4,5" not in objs2, claims2
        assert "execute/4" in objs2, claims2


if __name__ == "__main__":
    unittest.main()
