defmodule CS2.Consumer.Materializer do
  def materialize(items), do: Enum.map(items,&Map.put(&1,"authority","NONE"))
end
