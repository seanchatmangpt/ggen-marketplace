defmodule CS2.Consumer.Compat do
  def normalize(m), do: m|>Map.put_new("authority","NONE")|>Map.put_new("dependencies",[])
end
