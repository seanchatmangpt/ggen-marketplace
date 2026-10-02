"""The ash-extension installer template emits a valid, idempotent, merging `--target` patch.

Chicago style, no mocks: the real `ggen sync run` renders the real pack template from a real
RDF spec, and the generated Elixir is parsed by a real `elixir` and, when a compiled Igniter
dependency tree is present, executed against a real in-memory Igniter project.

Defect under test: the template inserted a bare `extensions: [...]` fragment with
`Igniter.Code.Common.add_code/3`, which parses a statement, so `--target` raised SyntaxError (and
could never merge into an existing `extensions:` list). The fixed template calls
`Spark.Igniter.add_extension/5`, the mechanism ash_graphlaw's installer tests prove.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# v26.9.30 consolidation lane 6: ash-extension-pack is the sole canonical identity
# (core's codegen/gates/support_subdir capabilities ported into it); the
# ash-extension-core-pack identity is retired delete-ready pending coordinator repoints.
PACKS = ("ash-extension-pack",)

# Read-only compiled Igniter/Spark/Ash tree used only to execute the generated task.
IGNITER_LIBS = Path("/Users/sac/ash_graphlaw/_build/test/lib")

ONTOLOGY = """\
@prefix aex: <http://seanchatmangpt.github.io/packs/ash-extension-core#> .
@prefix ex: <urn:ex:> .
ex:Spec a aex:AshExtensionSpec ;
    aex:packageName "ash_probe" ;
    aex:moduleName "AshProbe.Resource" ;
    aex:extensionTarget "resource" ;
    aex:singleExtensionKind "ash_probe" ;
    aex:taskModuleName "AshProbe" ;
    aex:formatterModule "AshProbe.Formatter" ;
    aex:installerRuntimeDep "wasmex|~> 0.15" ;
    aex:workflowReactor false ;
    aex:workflowReversible false ;
    aex:generatesReceiptedAction false ;
    aex:dualLevelFixture false ;
    aex:validateDelegateModule "AshProbe.Contract" ;
    aex:validateDelegateFunction "validate" .
ex:Sec a aex:DslSection ; aex:sectionOf ex:Spec ; aex:sectionName "probe" ; aex:sectionOrder 1 ;
    aex:sectionDescribe "probe section" .
"""

MIX_EXS = """\
defmodule Probe.MixProject do
  use Mix.Project
  def project, do: [app: :probe, version: "0.0.1", elixir: "~> 1.15", deps: [], consolidate_protocols: false]
end
"""

# Runs the generated installer task against in-memory Igniter projects and prints one JSON-ish
# line per observation. The preload of every beam is needed because Mix's loadpaths step inside
# Igniter drops the -pa paths this harness was started with.
HARNESS = r"""
Mix.start()
Mix.env(:test)
Code.compile_file("mix.exs")
{:ok, _} = Application.ensure_all_started(:igniter)
{:ok, _} = Application.ensure_all_started(:spark)
{:ok, _} = Application.ensure_all_started(:ash)
for b <- Path.wildcard(Path.join(System.fetch_env!("IGNITER_LIBS"), "*/ebin/*.beam")),
    do: :code.load_abs(String.to_charlist(Path.rootname(b)))
[file | _] = System.argv()
Code.compile_file(file)

plain = \"\"\"
defmodule My.Res do
  use Ash.Resource,
    domain: My.Domain,
    data_layer: Ash.DataLayer.Ets

  attributes do
    uuid_primary_key(:id)
  end
end
\"\"\"
listed = String.replace(plain, "data_layer: Ash.DataLayer.Ets", "data_layer: Ash.DataLayer.Ets,\n    extensions: [Other.Extension]")
path = "lib/my/res.ex"
content = fn ig -> ig.rewrite |> Rewrite.source!(path) |> Rewrite.Source.get(:content) end
run = fn src, argv -> Igniter.compose_task(Igniter.Test.test_project(files: %{path => src}), "ash_probe.install", argv) end
count = fn s, sub -> length(String.split(s, sub)) - 1 end

applied = content.(run.(plain, ["--target", "My.Res"]))
IO.puts("PARSES=" <> to_string(match?({:ok, _}, Code.string_to_quoted(applied))))
IO.puts("EXT_COUNT=" <> to_string(count.(applied, "AshProbe.Resource")))
IO.puts("BLOCK_COUNT=" <> to_string(count.(applied, "probe do")))
IO.puts("IDEMPOTENT=" <> to_string(content.(run.(applied, ["--target", "My.Res"])) == applied))
merged = content.(run.(listed, ["--target", "My.Res"]))
IO.puts("MERGE_OPTIONS=" <> to_string(count.(merged, "extensions:")))
IO.puts("MERGE_KEEPS_OTHER=" <> to_string(String.contains?(merged, "Other.Extension")))
IO.puts("MERGE_HAS_OURS=" <> to_string(String.contains?(merged, "AshProbe.Resource")))
bare = run.(plain, [])
untouched =
  case Rewrite.source(bare.rewrite, path) do
    {:ok, src} -> Rewrite.Source.get(src, :content) == plain
    _ -> true
  end

IO.puts("NOTARGET_UNTOUCHED=" <> to_string(untouched))
IO.puts("NOTARGET_NOTICE=" <> to_string(Enum.any?(bare.notices, &String.contains?(&1, "--target"))))
"""


def have(*tools: str) -> bool:
    return all(shutil.which(t) for t in tools)


def render_installer(pack: str, dest: Path) -> str:
    """Render the installer through real ggen, as a marketplace pack reference."""
    (dest / "templates").mkdir(parents=True)
    (dest / "ontology.ttl").write_text(ONTOLOGY, encoding="utf-8")
    packs = f'[packs]\n{pack} = {{ path = "{ROOT / "packs" / pack}" }}\n'
    (dest / "ggen.toml").write_text(
        '[project]\nname = "ash_probe"\n[ontology]\nsource = "ontology.ttl"\n' + packs +
        '[templates]\ndir = "templates"\n',
        encoding="utf-8",
    )
    r = subprocess.run(["ggen", "sync", "run"], cwd=dest, capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError((r.stdout + r.stderr)[-800:])
    return (dest / "lib/mix/tasks/ash_probe.install.ex").read_text(encoding="utf-8")


@unittest.skipUnless(have("ggen"), "BLOCKED: ggen not installed")
class InstallerTemplateEmission(unittest.TestCase):
    def render(self, pack: str) -> str:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return render_installer(pack, Path(tmp.name) / "proj")

    def test_target_patch_uses_spark_add_extension_not_a_bare_fragment(self) -> None:
        for pack in PACKS:
            with self.subTest(pack=pack):
                out = self.render(pack)
                self.assertIn(
                    "Spark.Igniter.add_extension(target_module, Ash.Resource, :extensions, AshProbe.Resource)", out)
                self.assertNotIn('add_code(zipper, "extensions:', out)
                self.assertNotIn("defp add_extension(", out)

    @unittest.skipUnless(have("elixir"), "BLOCKED: elixir not installed")
    def test_generated_task_parses_as_elixir(self) -> None:
        for pack in PACKS:
            with self.subTest(pack=pack):
                tmp = tempfile.TemporaryDirectory()
                self.addCleanup(tmp.cleanup)
                src = self.render(pack)
                f = Path(tmp.name) / "install.ex"
                f.write_text(src, encoding="utf-8")
                r = subprocess.run(
                    ["elixir", "-e", "Code.string_to_quoted!(File.read!(hd(System.argv()))); IO.puts(\"ok\")", str(f)],
                    capture_output=True, text=True)
                self.assertEqual((r.returncode, r.stdout.strip()), (0, "ok"), r.stderr[-600:])

    @unittest.skipUnless(have("elixir") and IGNITER_LIBS.is_dir(),
                         "BLOCKED: elixir or compiled igniter tree (ash_graphlaw _build) missing")
    def test_installer_runs_idempotently_and_merges_into_existing_extensions(self) -> None:
        for pack in PACKS:
            with self.subTest(pack=pack):
                tmp = tempfile.TemporaryDirectory()
                self.addCleanup(tmp.cleanup)
                work = Path(tmp.name)
                src = render_installer(pack, work / "proj")
                run_dir = work / "run"
                run_dir.mkdir()
                (run_dir / "mix.exs").write_text(MIX_EXS, encoding="utf-8")
                (run_dir / "inst.ex").write_text(src, encoding="utf-8")
                (run_dir / "harness.exs").write_text(HARNESS.replace('\\"\\"\\"', '"""'), encoding="utf-8")
                args = ["elixir"]
                for d in sorted(IGNITER_LIBS.glob("*/ebin")):
                    args += ["-pa", str(d)]
                r = subprocess.run(args + ["harness.exs", "inst.ex"], cwd=run_dir, capture_output=True, text=True,
                                   env={**os.environ, "IGNITER_LIBS": str(IGNITER_LIBS)})
                obs = dict(m.groups() for m in map(re.compile(r"^([A-Z_]+)=(.*)$").match, r.stdout.splitlines()) if m)
                self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-1200:])
                self.assertEqual(
                    obs,
                    {"PARSES": "true", "EXT_COUNT": "1", "BLOCK_COUNT": "1", "IDEMPOTENT": "true",
                     "MERGE_OPTIONS": "1", "MERGE_KEEPS_OTHER": "true", "MERGE_HAS_OURS": "true",
                     "NOTARGET_UNTOUCHED": "true", "NOTARGET_NOTICE": "true"},
                    r.stdout[-1200:])


if __name__ == "__main__":
    unittest.main()
