defmodule CS2.Consumer.Property.TopologyDeterministic do
 def check(xs), do: CS2.Consumer.Topology.order(xs)==CS2.Consumer.Topology.order(xs)
end
