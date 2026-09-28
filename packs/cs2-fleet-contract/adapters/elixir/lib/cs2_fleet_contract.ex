defmodule CS2FleetContract do
  @moduledoc """
  Runtime-neutral loader for the generated RFC-CS2-001 fleet contract.

  Consumer repositories depend on this adapter rather than re-declaring
  subject, authority ceiling, work IDs, or distribution targets.
  """

  @subject "https://chatman.ai/cs2#RFC-CS2-001"
  @schema "https://chatman.ai/cs2/fleet-contract/v1"

  def subject, do: @subject
  def schema, do: @schema

  def decode!(json, decoder) when is_binary(json) and is_function(decoder, 1) do
    contract = decoder.(json)
    assert_identity!(contract)
  end

  def assert_identity!(%{"contract_schema" => @schema, "consumers" => consumers} = contract)
      when is_list(consumers) do
    Enum.each(consumers, fn
      %{"subject" => @subject, "authority_ceiling" => "CONSTRUCT"} -> :ok
      row -> raise ArgumentError, "divergent CS2 consumer row: #{inspect(row)}"
    end)

    contract
  end

  def assert_identity!(contract) do
    raise ArgumentError, "divergent CS2 fleet contract: #{inspect(contract)}"
  end

  def for_repository(%{"consumers" => consumers}, repository) when is_binary(repository) do
    Enum.filter(consumers, &(&1["target_repository"] == repository))
  end

  def for_work(%{"consumers" => consumers}, work_id) when is_binary(work_id) do
    Enum.find(consumers, &(&1["work_id"] == work_id))
  end
end
