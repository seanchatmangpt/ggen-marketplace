defmodule CS2.Consumer.Receipt do
  def build(w), do: %{"workKey"=>w["workKey"],"sourceSha"=>w["sourceSha"],"authority"=>"NONE"}
end
