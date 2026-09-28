defmodule CS2.Consumer.Property.Idempotency do
  def check(x), do: CS2.Consumer.Idempotency.key(x)==CS2.Consumer.Idempotency.key(x)
end
