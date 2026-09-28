defmodule CS2.Consumer.Stress.Cycle do
 def build(n), do: Enum.map(1..n,fn i->%{"workKey"=>"w#{i}","dependencies"=>["w#{rem(i,n)+1}"]} end)
end
