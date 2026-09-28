defmodule CS2.Consumer.Bench.Materialize do
  def run(xs), do: CS2.Consumer.Materializer.materialize(xs)
end
