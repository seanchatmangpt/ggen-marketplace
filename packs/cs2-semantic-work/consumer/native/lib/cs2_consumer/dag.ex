defmodule CS2.Consumer.DAG do
  def dependencies(x), do: Map.get(x,"dependencies",[])
  def key(x), do: Map.fetch!(x,"workKey")
end
