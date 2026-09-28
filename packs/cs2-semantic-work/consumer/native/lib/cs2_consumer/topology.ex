defmodule CS2.Consumer.Topology do
  alias CS2.Consumer.Error
  def order(items) do
    by=Map.new(items,&{&1["workKey"],&1})
    deps=Map.new(items,&{&1["workKey"],MapSet.new(Map.get(&1,"dependencies",[]))})
    cond do
      Enum.any?(deps,fn {k,d}->MapSet.member?(d,k) end)->{:error,%Error{code:"self_dependency"}}
      Enum.any?(deps,fn {_,d}->Enum.any?(d,&(!Map.has_key?(by,&1))) end)->{:error,%Error{code:"missing_dependency"}}
      true->walk(by,deps,[])
    end
  end
  defp walk(by,deps,out) when map_size(deps)==0, do: {:ok,Enum.reverse(out)|>Enum.map(&Map.fetch!(by,&1))}
  defp walk(by,deps,out) do
    ready=deps|>Enum.filter(fn {_,d}->MapSet.size(d)==0 end)|>Enum.map(&elem(&1,0))|>Enum.sort()
    if ready==[], do: {:error,%Error{code:"dependency_cycle"}}, else: walk(by,drop(deps,ready),Enum.reverse(ready)++out)
  end
  defp drop(deps,ready), do: Enum.reduce(ready,deps,fn k,a->a|>Map.delete(k)|>Map.new(fn {x,d}->{x,MapSet.delete(d,k)} end) end)
end
