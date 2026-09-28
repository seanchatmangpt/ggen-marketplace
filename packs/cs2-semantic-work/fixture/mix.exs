defmodule Cs2SemanticWorkFixture.MixProject do
  use Mix.Project

  # Consumer fixture for packs/cs2-semantic-work. CS2_PACK_GENERATED is the
  # generated/cs2-semantic-work tree a real `ggen sync run` projected (elixir/*.ex
  # admission modules + the producer/consumer JSON projections), copied verbatim into
  # a capsule by scripts/cs2_pack_live_fixture.sh. MIX_BUILD_ROOT / MIX_DEPS_PATH also
  # point into that capsule, so no _build/, deps/, or generated copy lands inside the
  # pack directory (marketplace.py archives every visible file under a pack and
  # refuses symlinks). There is no lib/: the pack generates all code.
  def project do
    [
      app: :cs2_semantic_work_fixture,
      version: "0.1.0",
      elixir: "~> 1.18",
      start_permanent: false,
      elixirc_paths: [Path.join(generated_root(), "elixir")],
      deps: deps()
    ]
  end

  defp generated_root, do: System.get_env("CS2_PACK_GENERATED", "generated")

  def application, do: [extra_applications: [:logger]]

  defp deps, do: [{:jason, "~> 1.4"}]
end
