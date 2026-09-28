defmodule CS2.Consumer.Stress.Replay do
 def run(w,r,n), do: Enum.map(1..n,fn _->CS2.Consumer.Replay.envelope(w,r) end)
end
