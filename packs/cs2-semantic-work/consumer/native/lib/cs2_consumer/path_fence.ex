defmodule CS2.Consumer.PathFence do
  def allowed?(path,scopes) when is_binary(path), do: Enum.any?(scopes,&String.starts_with?(path,&1))
  def allowed?(_, _), do: false
end
