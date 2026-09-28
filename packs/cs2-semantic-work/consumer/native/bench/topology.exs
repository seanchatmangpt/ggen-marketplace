defmodule CS2.Consumer.Bench.Topology do
 def run(xs,n), do: Enum.each(1..n,fn _->CS2.Consumer.Topology.order(xs) end)
end
