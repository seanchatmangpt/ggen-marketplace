defmodule Mix.Tasks.MarketplaceCli.Validate do
  @moduledoc """
  `mix marketplace_cli.validate [--root PATH]` -- real
  `ex_noun_verb_cli`-based Igniter.Mix.Task, dispatching through the same
  `ExNounVerbCli.Dispatcher.dispatch/2` core the generic `mix
  ex_noun_verb_cli marketplace validate --root PATH` adapter uses, against
  the real `MarketplaceCli.Registry`. Defaults `--root` to this same
  marketplace checkout (`config :marketplace_cli, :marketplace_root`).
  """

  use Igniter.Mix.Task

  alias ExNounVerbCli.{Dispatcher, JsonOutput}

  @impl Igniter.Mix.Task
  def info(_argv, _composing_task) do
    %Igniter.Mix.Task.Info{
      group: :marketplace_cli,
      example: "mix marketplace_cli.validate --root /path/to/ggen-marketplace",
      schema: [root: :string]
    }
  end

  @impl Igniter.Mix.Task
  def igniter(igniter) do
    root =
      igniter.args.options[:root] || Application.fetch_env!(:marketplace_cli, :marketplace_root)

    case Dispatcher.dispatch(MarketplaceCli.Registry, ["marketplace", "validate", "--root", root]) do
      {:ok, %{line: line} = result} ->
        Mix.shell().info(line)
        envelope = JsonOutput.encode(:ok, Map.delete(result, :line))
        Igniter.add_notice(igniter, JsonOutput.encode_string(envelope))

      {:error, error} ->
        envelope = JsonOutput.encode(:error, error)
        Igniter.add_issue(igniter, JsonOutput.encode_string(envelope))
    end
  end
end
