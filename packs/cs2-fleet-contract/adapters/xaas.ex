defmodule GgenMarketplace.CS2.XaasAdapter do
  @moduledoc false
  def project(contract, ash_packet) when is_map(contract) and is_map(ash_packet), do: %{schema: "chatman.cs2.fleet-contract.v1", subject: "RFC-CS2-001", work_id: "CS2-WRK-013", repository: "seanchatmangpt/xaas", upstream: ash_packet, consumer: consumer(contract, "CS2-WRK-013")}
  defp consumer(contract, id), do: Enum.find(Map.get(contract, "consumers", []), %{}, &(Map.get(&1, "work_id") == id))
end
