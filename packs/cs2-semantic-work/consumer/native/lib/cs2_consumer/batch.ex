defmodule CS2.Consumer.Batch do
  alias CS2.Consumer.{Admission,Topology,Idempotency}
  def admit(items) do
    with {:ok,xs} <- each(items), {:ok,ordered} <- Topology.order(xs), do: {:ok,Enum.map(ordered,&Map.put(&1,"idempotencyKey",Idempotency.key(&1)))}
  end
  defp each(xs), do: Enum.reduce_while(xs,{:ok,[]},fn x,{:ok,a}->case Admission.admit(x) do {:ok,v}->{:cont,{:ok,[v|a]}}; e->{:halt,e} end end)|>case do {:ok,a}->{:ok,Enum.reverse(a)}; e->e end
end
