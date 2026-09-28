defmodule CS2.Consumer.Property.DigestBinding do
 def check(x), do: CS2.Consumer.Digest.bound?(x,CS2.Consumer.Digest.sha256(x))
end
