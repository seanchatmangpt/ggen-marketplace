defmodule CrossSpecScopingTest do
  @moduledoc """
  Falsifier for per-spec query scoping in packs/ash-extension-pack.

  qualification/consumer.ttl declares two extension specs (PipelineProbe,
  LedgerProbe) next to the pack ontology's three worked specs, all in one union
  graph. ggen evaluates each template's named `sparql:` results once against that
  whole graph, so an unscoped query renders every spec's sections, entities,
  getters, verifiers and steps into every other spec's modules. Each assertion
  here reads either the compiled generated modules (runtime introspection) or the
  generated source files the capsule compiled (ASH_PACK_GENERATED).
  """
  use ExUnit.Case, async: true

  # Spec-owned vocabulary, straight from qualification/consumer.ttl and ontology.ttl.
  @owned %{
    "pipeline_probe" => ~w(pipeline stage stage_index admit deliver seal),
    "ledger_probe" => ~w(ledger posting posting_index currency balanced_postings reserve post settle),
    "notification_extension" => ~w(notification channel channel_index seal_receipt),
    "audit_trail" => ~w(audit unique_event_name valid_projection),
    "ash_r2rml" => ~w(r2rml sparql)
  }

  defp generated_dir do
    System.get_env("ASH_PACK_GENERATED") ||
      flunk("ASH_PACK_GENERATED unset: run scripts/ash_pack_live_fixture.sh")
  end

  defp sources(package) do
    Path.join([generated_dir(), package, "**", "*.ex"])
    |> Path.wildcard()
    |> Enum.map(&{&1, File.read!(&1)})
  end

  defp exclusive(package) do
    others = @owned |> Map.delete(package) |> Map.values() |> List.flatten()
    Enum.uniq(others) -- @owned[package]
  end

  test "each spec's generated files mention no other spec's exclusive names" do
    for package <- ["pipeline_probe", "ledger_probe"],
        {path, source} <- sources(package),
        name <- exclusive(package) do
      refute source =~ ~r/[:@]#{name}\b/, "#{path} leaks :#{name} from another spec"
    end
  end

  test "Spark sections of each generated extension are its own" do
    assert Enum.map(PipelineProbe.sections(), & &1.name) == [:pipeline]
    assert Enum.map(LedgerProbe.Resource.sections(), & &1.name) == [:ledger]
    assert Enum.map(NotificationExtension.Resource.sections(), & &1.name) == [:notification]
    assert Enum.map(AshR2RML.Resource.sections(), & &1.name) == [:r2rml, :sparql]
  end

  defp exports?(module, fun, arity) do
    Code.ensure_loaded!(module)
    function_exported?(module, fun, arity)
  end

  test "Info getters are generated only for the spec that declares them" do
    assert exports?(PipelineProbe.Info, :stage_index, 1)
    refute exports?(PipelineProbe.Info, :posting_index, 1)
    refute exports?(PipelineProbe.Info, :channel_index, 1)
    assert exports?(LedgerProbe.Resource.Info, :posting_index, 1)
    refute exports?(LedgerProbe.Resource.Info, :stage_index, 1)
    refute exports?(LedgerProbe.Resource.Info, :audit, 1)
  end

  test "each Reactor pipeline carries only its own spec's steps" do
    steps = fn reactor -> reactor |> Reactor.Info.to_struct!() |> Map.fetch!(:steps) |> Enum.map(& &1.name) |> Enum.sort() end
    assert steps.(PipelineProbe.Reactor.Pipeline) == [:admit, :deliver, :seal]
    assert steps.(LedgerProbe.Resource.Reactor.Pipeline) == [:post, :reserve, :settle]
  end
end
