defmodule CS2.Consumer.ProjectionFence do
  @known ~w(WorkItem WorkBatch)
  def allowed?(x), do: x in @known
end
