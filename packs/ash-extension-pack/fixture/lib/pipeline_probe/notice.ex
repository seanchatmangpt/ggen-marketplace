defmodule PipelineProbe.Notice do
  @moduledoc """
  Consumer-owned resource the generated `PipelineProbe.ReceiptedAction` wraps.
  ETS data layer: real Ash actions, real rows, no database. `private? true` gives
  each test process its own table, so tests start empty without racing a
  shared table's teardown.
  """
  use Ash.Resource,
    domain: PipelineProbe.Domain,
    data_layer: Ash.DataLayer.Ets

  ets do
    private? true
  end

  actions do
    defaults [:read]

    create :create do
      accept [:channel, :body]
    end
  end

  attributes do
    uuid_primary_key :id
    attribute :channel, :string, allow_nil?: false, public?: true
    attribute :body, :string, allow_nil?: false, public?: true
  end
end
