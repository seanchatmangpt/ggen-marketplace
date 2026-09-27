defmodule GgenMarketplace.CS2.AshA2AAdapter do
  @moduledoc false
  def project(contract) when is_map(contract), do: %{schema: "chatman.cs2.fleet-contract.v1", subject: "RFC-CS2-001", work_id: "CS2-WRK-012", repository: "seanchatmangpt/ash_a2a", consumer: consumer(contract, "CS2-WRK-012")}
  defp consumer(contract, id), do: Enum.find(Map.get(contract, "consumers", []), %{}, &(Map.get(&1, "work_id") == id))
end
