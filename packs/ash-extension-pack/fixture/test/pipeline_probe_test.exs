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

  describe "generated Reactor pipeline + generated step modules" do
    # The step modules are projected by templates/reactor_step.ex.tmpl; the run order
    # is read from the real [:reactor, :step, :run, :start] telemetry that the
    # generated pipeline's Reactor.Middleware.Telemetry emits.
    setup do
      test_pid = self()
      handler = "pipeline-probe-order-#{System.unique_integer([:positive])}"

      :ok =
        :telemetry.attach(
          handler,
          [:reactor, :step, :run, :start],
          fn _event, _measurements, %{step: step}, _ -> send(test_pid, {:step_ran, step.name}) end,
          nil
        )

      on_exit(fn -> :telemetry.detach(handler) end)
      :ok
    end

    test "runs the declared steps in aex:stepOrder and returns the return step" do
      assert {:ok, %{step: :seal, arguments: %{}}} =
               Reactor.run(PipelineProbe.Reactor.Pipeline, %{}, %{}, async?: false)

      order =
        for _ <- 1..3 do
          assert_receive {:step_ran, step}
          step
        end

      assert order == [:admit, :deliver, :seal]
      refute_receive {:step_ran, _}
    end

    test "each generated step returns its own name and resolved arguments" do
      for {module, name} <- [
            {PipelineProbe.Reactor.Steps.Admit, :admit},
            {PipelineProbe.Reactor.Steps.Deliver, :deliver},
            {PipelineProbe.Reactor.Steps.Seal, :seal}
          ] do
        assert {:ok, %{step: ^name, arguments: %{x: 1}}} = module.run(%{x: 1}, %{}, [])
      end
    end

    test "compensate/4 is generated exactly where aex:stepHasCompensate is true" do
      # ledger_probe/reserve and notification_extension/deliver declare it; the
      # PipelineProbe steps and ledger_probe/post, settle do not.
      for module <- [
            LedgerProbe.Resource.Reactor.Steps.Reserve,
            LedgerProbe.Resource.Reactor.Steps.Post,
            NotificationExtension.Resource.Reactor.Steps.Deliver,
            PipelineProbe.Reactor.Steps.Seal
          ],
          do: Code.ensure_loaded!(module)

      assert function_exported?(LedgerProbe.Resource.Reactor.Steps.Reserve, :compensate, 4)
      assert :ok = LedgerProbe.Resource.Reactor.Steps.Reserve.compensate(:boom, %{}, %{}, [])
      assert function_exported?(NotificationExtension.Resource.Reactor.Steps.Deliver, :compensate, 4)
      refute function_exported?(LedgerProbe.Resource.Reactor.Steps.Post, :compensate, 4)
      refute function_exported?(PipelineProbe.Reactor.Steps.Seal, :compensate, 4)
    end
  end
end
