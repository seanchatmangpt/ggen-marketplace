defmodule GreetCli.MixProject do
  use Mix.Project

  def project do
    [
      app: :greet_cli,
      version: "0.1.0",
      elixir: "~> 1.17",
      start_permanent: Mix.env() == :prod,
      deps: deps(),
      escript: escript()
    ]
  end

  def application do
    [
      extra_applications: [:logger]
    ]
  end

  defp deps do
    [
      {:ex_noun_verb_cli, "~> 26.9"}
    ]
  end

  defp escript do
    [main_module: ExNounVerbCli.Escript]
  end
end
