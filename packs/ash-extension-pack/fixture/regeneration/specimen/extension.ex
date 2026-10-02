# ------------------------------------------------------------------
# GENERATED -- regeneration specimen extension.
# Source of truth: the semantic facts (facts.exs / the pack ontology).
# This file is NEVER authoritative. A byte on disk that differs from a
# fresh render from the current facts is a violation, not a truth.
# ------------------------------------------------------------------
defmodule RegenerationSpecimen.Resource do
  @moduledoc """
  Generated regeneration specimen extension.

  One Spark-shaped extension surface, derived entirely from declared
  facts: one section (:audit), two entities (:event, :projection),
  two verifiers, one Info getter quadruple, a declared Reactor step
  graph, and an idempotent installer.
  """

  @extension_target :resource

  @sections [
    %{
      name: :audit,
      order: 1,
      describe: "Audit event and projection declarations.",
      singleton_entity_keys: [],
      entities: [
    %{
      name: :event,
      order: 1,
      struct: "RegenerationSpecimen.Dsl.Event",
      identifier: nil,
      args: [],
      fields: [
        %{name: :name, type: :atom, required: true, default: nil},
        %{name: :description, type: :string, required: false, default: nil},
      ]
    },
    %{
      name: :projection,
      order: 2,
      struct: "RegenerationSpecimen.Dsl.Projection",
      identifier: :attribute,
      args: [:attribute],
      fields: [
        %{name: :attribute, type: :atom, required: true, default: nil},
        %{name: :strategy, type: {:one_of, [:eager, :lazy]}, required: false, default: :eager},
      ]
    },
      ]
    }
  ]

  @verifiers [
      {:unique_event_name, "Every :audit event name must be unique within the resource."},
      {:valid_projection, "Every :audit projection attribute must reference an attribute that actually exists on the resource."},
  ]

  @info_getters [
      %{name: :audit_index, source_section: :audit},
  ]

  @steps [
    %{
      name: :admit,
      order: 1,
      module: "RegenerationSpecimen.Reactor.Steps.Admit",
      wait_for: [],
      max_retries: 0,
      has_compensate: false,
      is_return: false,
      scope: :regeneration_specimen
    },
    %{
      name: :deliver,
      order: 2,
      module: "RegenerationSpecimen.Reactor.Steps.Deliver",
      wait_for: [:admit],
      max_retries: 3,
      has_compensate: true,
      is_return: false,
      scope: :regeneration_specimen
    },
    %{
      name: :seal_receipt,
      order: 3,
      module: "RegenerationSpecimen.Reactor.Steps.SealReceipt",
      wait_for: [:deliver],
      max_retries: 0,
      has_compensate: false,
      is_return: true,
      scope: :regeneration_specimen
    }
  ]

  @persist_after [
      "Ash.Resource.Transformers.CachePrimaryKey",
      "Ash.Resource.Transformers.SetRelationshipInformation",
  ]

  @single_extension_kinds [:regeneration_specimen]

  @installer_target "RegenerationSpecimen.Resource"

  def extension_target, do: @extension_target

  def sections, do: @sections

  def entities do
    Enum.flat_map(@sections, & &1.entities)
  end

  def verifiers, do: @verifiers

  def info_getters, do: @info_getters

  def steps, do: @steps

  def persist_after, do: @persist_after

  def single_extension_kinds, do: @single_extension_kinds

  def installer_target, do: @installer_target

  @doc """
  Declared Info getter quadruple dispatch: every getter resolves to the
  section its `source_section` fact names -- no runtime drift between
  declared and effective sources.
  """
  def do_info_get(_dsl_state, getter) do
    case Enum.find(@info_getters, &(&1.name == getter)) do
      nil ->
        {:error, :unknown_getter}

      getter_decl ->
        {:ok, Enum.find(@sections, &(&1.name == getter_decl.source_section))}
    end
  end

  @doc """
  The installer, modeled on the pack's Igniter installer law: idempotent
  -- running it against an already-installed dsl_state is a no-op.
  """
  def install(dsl_state) do
    dsl_state
    |> Map.put_new(:regeneration_specimen_installed, true)
    |> Map.put_new(:installed_targets, [@installer_target])
    |> Map.put_new(:installed_single_extension_kinds, @single_extension_kinds)
  end
end
