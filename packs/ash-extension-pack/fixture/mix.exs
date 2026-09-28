defmodule PipelineProbe.MixProject do
  use Mix.Project

  # Consumer fixture for packs/ash-extension-pack. lib/generated/ is written by
  # scripts/ash_pack_live_fixture.sh from a real `ggen sync run`; everything else
  # under lib/ is consumer-owned code the pack does not generate (the Ash
  # resource a receipted action wraps, and the Reactor step implementations the
  # generated pipeline references by module name).
  def project do
    [
      app: :pipeline_probe,
      version: "0.1.0",
      elixir: "~> 1.18",
      start_permanent: false,
      elixirc_paths: ["lib", generated_path()],
      deps: deps()
    ]
  end

  # scripts/ash_pack_live_fixture.sh points ASH_PACK_GENERATED (and MIX_BUILD_ROOT /
  # MIX_DEPS_PATH) into its capsule so no build output, dependency tree, or generated
  # copy ever lands inside the pack directory (marketplace.py archives every visible
  # file under a pack and refuses symlinks, which _build/ is full of).
  defp generated_path, do: System.get_env("ASH_PACK_GENERATED", "lib/generated")

  def application, do: [extra_applications: [:logger, :crypto]]

  defp deps do
    [
      {:ash, "~> 3.33"},
      {:reactor, "~> 1.0"}
    ]
  end
end
