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
        assert items["hidden"]["is_public"] is False  # @doc false: emitted, flagged internal
        assert "secret" not in items  # defp: excluded from the surface entirely
        assert items["visible"]["is_public"] is True
        assert items["shown"]["is_public"] is True

    def test_multiline_def_head_captures_arity(self):
        # Witnessed: beam4pm_deviation_admission.ex `def admit_deviation(`
        # heads split across lines lost arity (extracted /0, actually /5).
        src = (
            "defmodule Demo do\n"
            "  @ontology_path \"x.ttl\"\n"
            "  def admit_deviation(\n"
            "        result,\n"
            "        reference_trace_id,\n"
            "        candidate_trace_id,\n"
            "        ontology_path \\\\ @ontology_path,\n"
            "        opts \\\\ []\n"
            "      ) do\n"
            "    :ok\n"
            "  end\n"
            "\n"
            "  def single_line(a, b), do: {a, b}\n"
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
        assert items["admit_deviation"]["signature"] == "admit_deviation/5"
        assert items["single_line"]["signature"] == "single_line/2"

    def test_multiline_def_head_nested_parens_and_inline_default(self):
        # Defaults with tuple/paren nesting must not terminate the head scan.
        src = (
            "defmodule Demo do\n"
            "  def handle(\n"
            "        %{a: 1},\n"
            "        opts \\\\ [timeout: Application.fetch_env!(:app, :t)]\n"
            "      ) do\n"
            "    :ok\n"
            "  end\n"
            "end\n"
        )
        repo = mkrepo({"mix.exs": "defmodule Demo.MixProject do\n  def project, do: []\nend\n", "lib/demo.ex": src})
        code = g.extract_code(repo)
        items = [
            it
            for m in code["modules"]
            for it in m["items"]
            if it["kind"] == "function"
        ]
        assert len(items) == 1
        assert items[0]["signature"] == "handle/2"

    def test_multiline_def_head_without_paren_on_first_line(self):
        src = (
            "defmodule Demo do\n"
            "  def long_name\n"
            "  (\n"
            "        a, b\n"
            "  ) do\n"
            "  end\n"
            "end\n"
        )
        repo = mkrepo({"mix.exs": "defmodule Demo.MixProject do\n  def project, do: []\nend\n", "lib/demo.ex": src}
        )
        code = g.extract_code(repo)
        items = [
            it
            for m in code["modules"]
            for it in m["items"]
            if it["kind"] == "function"
        ]
        assert len(items) == 1
        assert items[0]["signature"] == "long_name/2"

    def test_per_clause_duplicates_deduped_with_clause_count(self):
        # Witnessed: beam4pm_codec.ex emits `from_map/2` once per clause
        # (x693); the surface must carry one item per name/arity with the
        # clause count noted.
        src = (
            "defmodule Demo do\n"
            "  def from_map(:a, m) when is_map(m), do: m\n"
            "  def from_map(:b, m), do: m\n"
            "  def from_map(:c, m), do: m\n"
            "  def from_map(other, m), do: {other, m}\n"
            "  def to_map(x, m), do: {x, m}\n"
            "end\n"
        )
        repo = mkrepo({"mix.exs": "defmodule Demo.MixProject do\n  def project, do: []\nend\n", "lib/demo.ex": src})
        code = g.extract_code(repo)
        items = [
            it
            for m in code["modules"]
            for it in m["items"]
            if it["kind"] == "function"
        ]
        from_map = [it for it in items if it["ident"] == "from_map"]
        assert len(from_map) == 1
        assert from_map[0]["signature"] == "from_map/2"
        assert from_map[0]["clauses"] == 4
        to_map = [it for it in items if it["ident"] == "to_map"]
        assert len(to_map) == 1 and "clauses" not in to_map[0]

    def test_defp_excluded_from_public_surface(self):
        # Witnessed: beam4pm_ocel_ingest.ex `defp handle_ingest(conn, "ocel_event")`
        # clauses were emitted as a public-looking `handle_ingest/2` item.
        src = (
            "defmodule Demo do\n"
            "  def public_fn(a), do: a\n"
            "  defp handle_ingest(conn, \"ocel_event\"), do: conn\n"
            "  defp handle_ingest(conn, \"ocel_object\"), do: conn\n"
            "end\n"
        )
        repo = mkrepo({"mix.exs": "defmodule Demo.MixProject do\n  def project, do: []\nend\n", "lib/demo.ex": src})
        code = g.extract_code(repo)
        items = [
            it
            for m in code["modules"]
            for it in m["items"]
            if it["kind"] == "function"
        ]
        assert [it["ident"] for it in items] == ["public_fn"]

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


class StructSignatureTest(unittest.TestCase):
    """DOC-HDIT v2 struct/enum field extraction: the degenerate-signature
    class (struct/enum/interface/type rows whose signature column is empty
    or name-only) must be populated from real source members."""

    def _items(self, code):
        return {
            (it["kind"], it["ident"]): it
            for m in code["modules"]
            for it in m["items"]
        }

    def test_rust_struct_and_enum_signatures(self):
        repo = mkrepo({
            "Cargo.toml": '[package]\nname = "demo"\nversion = "0.1.0"\n',
            "src/lib.rs": (
                "pub struct Config { pub name: String, retries: u32 }\n"
                "pub struct Wrapped(pub u32);\n"
                "pub enum Color { Red, Green, Mixed(u8, u8), Fancy { code: u16 } }\n"
            ),
        })
        items = self._items(g.extract_code(repo))
        assert items[("struct", "Config")]["signature"] == (
            "Config { pub name: String, retries: u32 }"
        )
        assert items[("struct", "Wrapped")]["signature"] == "Wrapped { pub u32 }"
        assert items[("enum", "Color")]["signature"] == (
            "Color { Red, Green, Mixed(u8, u8), Fancy { code: u16 } }"
        )

    def test_rust_unit_struct_and_trait_stay_unpopulated(self):
        repo = mkrepo({
            "Cargo.toml": '[package]\nname = "demo"\nversion = "0.1.0"\n',
            "src/lib.rs": "pub struct Marker;\npub trait Paint { fn paint(&self); }\n",
        })
        items = self._items(g.extract_code(repo))
        assert items[("struct", "Marker")]["signature"] == ""
        assert items[("trait", "Paint")]["signature"] == ""

    def test_elixir_defstruct_and_atom_type(self):
        src = (
            "defmodule Demo.State do\n"
            "  @type color :: :red | :green | :blue\n"
            "  defstruct [:name, retries: 0]\n"
            "  def new(), do: nil\n"
            "end\n"
        )
        repo = mkrepo({
            "mix.exs": "defmodule Demo.MixProject do\n  def project, do: []\nend\n",
            "lib/demo.ex": src,
        })
        items = self._items(g.extract_code(repo))
        assert items[("struct", "Demo.State")]["signature"] == (
            "defstruct name, retries: 0"
        )
        assert items[("type", "color")]["signature"] == (
            "@type color :: :red | :green | :blue"
        )

    def test_elixir_multiline_atom_type_folds_continuations(self):
        src = (
            "defmodule Demo.State do\n"
            "  @type mode ::\n"
            "    | :fast\n"
            "    | :slow\n"
            "  def go(), do: nil\n"
            "end\n"
        )
        repo = mkrepo({
            "mix.exs": "defmodule Demo.MixProject do\n  def project, do: []\nend\n",
            "lib/demo.ex": src,
        })
        items = self._items(g.extract_code(repo))
        assert items[("type", "mode")]["signature"] == "@type mode :: | :fast | :slow"

    def test_ts_interface_enum_type_signatures(self):
        import gen_doc_surface_ts as ts
        repo = mkrepo({
            "src/types.ts": (
                'export interface Options { name: string; retries?: number; '
                'cb: (a: number, b: string) => void; }\n'
                'export enum Color { Red, Green = 2, Blue }\n'
                'export type Mode = "fast" | "slow";\n'
            ),
        })
        code = ts.extract_code(repo)
        items = {
            (it["kind"], it["ident"]): it for m in code["modules"] for it in m["items"]
        }
        assert items[("interface", "Options")]["signature"] == (
            "Options { name: string, retries?: number, "
            "cb: (a: number, b: string) => void }"
        )
        assert items[("enum", "Color")]["signature"] == "Color { Red, Green = 2, Blue }"
        assert items[("type", "Mode")]["signature"] == 'Mode = "fast" | "slow"'


if __name__ == "__main__":
    unittest.main()
