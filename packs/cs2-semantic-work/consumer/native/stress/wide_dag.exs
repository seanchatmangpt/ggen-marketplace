defmodule CS2.Consumer.Stress.WideDAG do
  def build(n), do: Enum.map(1..n,&%{"workKey"=>"w#{&1}"})
end
