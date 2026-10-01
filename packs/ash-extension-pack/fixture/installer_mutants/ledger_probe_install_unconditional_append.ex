defmodule Mix.Tasks.LedgerProbe.Install do
  @moduledoc """
  ANTI-VACUITY MUTANT (lane C7, igniter idempotence court).

  Deliberately non-idempotent: every run rewrites
  lib/spark_closure_consumer/example/post.ex with an unconditional content
  replace, so a second `mix ledger_probe.install` run always produces a byte
  diff. The court, run with AEX_INSTALLER_MUTANT pointing at this file, MUST
  fail the repeat-install scenario -- if it passes, the court is vacuous.
  """
  use Igniter.Mix.Task

  @impl true
  def info(_argv, _composing_task) do
    %Igniter.Mix.Task.Info{
      group: :ledger_probe,
      example: "mix ledger_probe.install --target SparkClosureConsumer.Example.Post",
      positional: [],
      schema: [target: :string],
      required: []
    }
  end

  @impl true
  def igniter(igniter) do
    igniter
    |> Igniter.Project.Formatter.import_dep(:ledger_probe)
    |> Igniter.Project.Formatter.add_formatter_plugin(LedgerProbe.Formatter)
    |> Igniter.update_file("lib/spark_closure_consumer/example/post.ex", fn source ->
      Rewrite.Source.update(source, :content, fn content ->
        # MUTANT: appends unconditionally -- a second run prepends ANOTHER copy,
        # producing a byte diff (the real installer merges idempotently instead).
        if String.contains?(content, "extensions: [") do
          String.replace(content, "extensions: [", "extensions: [LedgerProbe.Resource, ")
        else
          String.replace(
            content,
            "data_layer: Ash.DataLayer.Ets",
            "data_layer: Ash.DataLayer.Ets,\n    extensions: [LedgerProbe.Resource]"
          )
        end
      end)
    end)
  end
end
