defmodule CS2.Consumer.Compat.LegacyDependencies do
  def adapt(m), do: Map.put_new(m,"dependencies",[])
end
