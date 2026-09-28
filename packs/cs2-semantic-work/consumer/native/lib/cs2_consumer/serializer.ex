defmodule CS2.Consumer.Serializer do
  def encode(map), do: inspect(map,limit: :infinity,printable_limit: :infinity)
end
