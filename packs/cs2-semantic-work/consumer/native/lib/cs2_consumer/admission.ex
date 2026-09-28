defmodule CS2.Consumer.Admission do
  @required ~w(workKey subject sourceRepo sourceSha objective acceptance falsifier nextEdge pathScope projectionType)
  def admit(m), do: if(Enum.all?(@required,&Map.has_key?(m,&1)) and Map.get(m,"authority","NONE")=="NONE",do:{:ok,m},else:{:error,:refused})
end
