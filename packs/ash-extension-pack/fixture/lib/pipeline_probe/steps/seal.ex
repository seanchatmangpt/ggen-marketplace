defmodule PipelineProbe.Reactor.Steps.Seal do
  @moduledoc """
  Consumer-owned implementation of the `:seal` step that the generated
  `PipelineProbe.Reactor.Pipeline` names. It reports its execution to the
  process in `context[:observer]` so the fixture can read the real run order.
  """
  use Reactor.Step

  @impl true
  def run(_arguments, context, _options) do
    if observer = context[:observer], do: send(observer, {:step_ran, :seal})
    {:ok, :seal}
  end
end
