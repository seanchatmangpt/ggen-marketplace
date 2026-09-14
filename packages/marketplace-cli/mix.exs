defmodule MarketplaceCli.MixProject do
  use Mix.Project

  def project do
    [
      app: :marketplace_cli,
      version: "26.9.11",
      elixir: "~> 1.17",
      start_permanent: Mix.env() == :prod,
      deps: deps(),
      elixirc_paths: elixirc_paths(Mix.env())
    ]
  end

  def application do
    [extra_applications: [:logger]]
  end

  defp elixirc_paths(:test), do: ["lib", "test/support"]
  defp elixirc_paths(_), do: ["lib"]

  # Real consumer application proving ex_noun_verb_cli's milestone-2 design:
  # a GraphProvider wraps ggen_igniter's real Ontology.load!/1 + Query.run/2,
  # both pulled in as real path: dependencies pointing at their real sibling
  # checkouts (per the design spec's explicit decoupling: ex_noun_verb_cli
  # itself never depends on ggen_igniter -- only a consumer does).
  #
  # Neither sibling repo is vendored under this repo (no submodule, no fixed
  # relative checkout location) and ex_noun_verb_cli has no known upstream
  # git remote on this machine, so a relative path: or a github: dependency
  # would be either wrong or unverifiable. The portable fix is to resolve
  # each checkout's location from an env var, defaulting to the previous
  # hardcoded absolute path so this still resolves unchanged on machines
  # that already have these siblings checked out at that location -- set
  # EX_NOUN_VERB_CLI_PATH / GGEN_IGNITER_PATH to override elsewhere.
  defp deps do
    [
      {:ex_noun_verb_cli, path: System.get_env("EX_NOUN_VERB_CLI_PATH", "/Users/sac/ex_noun_verb_cli")},
      {:ggen_igniter, path: System.get_env("GGEN_IGNITER_PATH", "/Users/sac/ggen_igniter")},
      {:igniter, "~> 0.8"},
      {:jason, "~> 1.4"}
    ]
  end
end
