defmodule PipelineProbeTest do
  @moduledoc """
  Executes the Elixir that a real `ggen sync run` projected from
  packs/ash-extension-pack (qualification/consumer.ttl's PipelineProbeSpec).
  Chicago-style: real Ash actions on a real ETS data layer, a real Reactor run;
  every assertion reads returned values, receipt rows, or resource rows.
  """
  use ExUnit.Case, async: false

  alias PipelineProbe.{Notice, Receipt, ReceiptedAction}

  @payload %{channel: "email", body: "hello"}

  setup do
    Receipt.reset!()
    :ok
  end

  defp rows, do: Ash.read!(Notice)

  describe "generated ReceiptedAction" do
    test "same key + same payload replays the sealed receipt without re-running" do
      assert {:ok, first, %Receipt{status: :sealed}} =
               ReceiptedAction.run(Notice, :create, @payload, "evt-1")

      assert {:ok, replayed, %Receipt{status: :replayed} = receipt} =
               ReceiptedAction.run(Notice, :create, @payload, "evt-1")

      assert replayed.id == first.id
      assert receipt.fingerprint == ReceiptedAction.fingerprint(Notice, :create, nil, @payload)
      assert [%Notice{id: id}] = rows()
      assert id == first.id
      assert {:ok, %Receipt{status: :sealed}} = Receipt.find_by_key("evt-1")
    end

    test "same key + different payload is an idempotency conflict" do
      assert {:ok, _, _} = ReceiptedAction.run(Notice, :create, @payload, "evt-2")

      assert {:error, {:idempotency_conflict, "evt-2"}} =
               ReceiptedAction.run(Notice, :create, %{@payload | body: "other"}, "evt-2")

      assert [%Notice{body: "hello"}] = rows()
    end

    test "a missing key is refused before admission" do
      assert {:error, :idempotency_key_required} =
               ReceiptedAction.run(Notice, :create, @payload, nil)

      assert rows() == []
    end

    test "a failed action records a failed receipt and the key is re-admittable" do
      assert {:error, %Ash.Error.Invalid{}} =
               ReceiptedAction.run(Notice, :create, %{channel: "email"}, "evt-3")

      assert {:ok, %Receipt{status: :failed}} = Receipt.find_by_key("evt-3")
      assert {:ok, _, %Receipt{status: :sealed}} =
               ReceiptedAction.run(Notice, :create, @payload, "evt-3")

      assert length(rows()) == 1
    end
  end

  describe "generated Reactor pipeline" do
    test "runs the declared steps in aex:stepOrder and returns the return step" do
      assert {:ok, :seal} =
               Reactor.run(PipelineProbe.Reactor.Pipeline, %{}, %{observer: self()})

      order =
        for _ <- 1..3 do
          assert_receive {:step_ran, step}
          step
        end

      assert order == [:admit, :deliver, :seal]
      refute_receive {:step_ran, _}
    end
  end
end
