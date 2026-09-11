defmodule Mix.Tasks.MarketplaceCli.Catalog do
  @moduledoc """
  `mix marketplace_cli.catalog [--root PATH]` -- real
  `ex_noun_verb_cli`-based Igniter.Mix.Task, dispatching through
  `ExNounVerbCli.Dispatcher.dispatch/2` against `MarketplaceCli.Registry`.
  Prints the full catalog JSON to stdout, mirroring
  `python3 scripts/marketplace.py catalog`.
  """

  use Igniter.Mix.Task

  alias ExNounVerbCli.{Dispatcher, JsonOutput}

  @impl Igniter.Mix.Task
  def info(_argv, _composing_task) do
    %Igniter.Mix.Task.Info{
      group: :marketplace_cli,
      example: "mix marketplace_cli.catalog --root /path/to/ggen-marketplace",
      schema: [root: :string]
    }
  end

  @impl Igniter.Mix.Task
  def igniter(igniter) do
    root = igniter.args.options[:root] || Application.fetch_env!(:marketplace_cli, :marketplace_root)

    case Dispatcher.dispatch(MarketplaceCli.Registry, ["marketplace", "catalog", "--root", root]) do
      {:ok, payload} ->
        json = Jason.encode!(payload, pretty: true)
        Mix.shell().info(json)
        Igniter.add_notice(igniter, JsonOutput.encode_string(JsonOutput.encode(:ok, %{"printed" => true})))

      {:error, error} ->
        envelope = JsonOutput.encode(:error, error)
        Igniter.add_issue(igniter, JsonOutput.encode_string(envelope))
    end
  end
end
