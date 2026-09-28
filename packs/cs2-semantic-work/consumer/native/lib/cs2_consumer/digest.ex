defmodule CS2.Consumer.Digest do
  def sha256(data), do: :crypto.hash(:sha256,data)|>Base.encode16(case: :lower)
  def bound?(data,digest), do: sha256(data)==digest
end
