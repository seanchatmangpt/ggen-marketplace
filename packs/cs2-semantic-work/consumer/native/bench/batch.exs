defmodule CS2.Consumer.Bench.Batch do
 def run(xs,n), do: Enum.each(1..n,fn _->CS2.Consumer.Batch.admit(xs) end)
end
