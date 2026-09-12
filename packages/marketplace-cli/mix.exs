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
  # checkouts on this machine (per the design spec's explicit decoupling:
  # ex_noun_verb_cli itself never depends on ggen_igniter -- only a consumer
  # does).
  defp deps do
    [
      {:ex_noun_verb_cli, path: "/Users/sac/ex_noun_verb_cli"},
      {:ggen_igniter, path: "/Users/sac/ggen_igniter"},
      {:igniter, "~> 0.8"},
      {:jason, "~> 1.4"}
    ]
  end
end
