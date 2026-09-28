defmodule CS2.Consumer.Replay do
  def envelope(work,receipt), do: %{"workKey"=>work["workKey"],"receipt"=>receipt,"authority"=>"NONE","doAuthority"=>false}
end
