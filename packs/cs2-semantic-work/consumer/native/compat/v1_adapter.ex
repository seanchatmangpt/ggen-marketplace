defmodule CS2.Consumer.Compat.V1Adapter do
  def adapt(m), do: Map.put_new(m,"authority","NONE")
end
