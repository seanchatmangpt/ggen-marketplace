defmodule CS2.Consumer.Refusal do
  def envelope(code,field\\nil), do: %{"status"=>"REFUSED","code"=>code,"field"=>field,"authority"=>"NONE"}
end
