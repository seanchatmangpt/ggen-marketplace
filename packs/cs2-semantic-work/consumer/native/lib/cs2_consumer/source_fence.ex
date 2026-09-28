defmodule CS2.Consumer.SourceFence do
  def exact?(work,repo,sha), do: work["sourceRepo"]==repo and work["sourceSha"]==sha
end
