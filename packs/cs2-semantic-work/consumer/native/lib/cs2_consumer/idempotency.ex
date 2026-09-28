defmodule CS2.Consumer.Idempotency do
  def key(x), do: :crypto.hash(:sha256,Enum.join([x["sourceRepo"],x["sourceSha"],x["workKey"]],":")) |> Base.encode16(case: :lower)
end
