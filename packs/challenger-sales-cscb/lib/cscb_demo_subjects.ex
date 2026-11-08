defmodule CscbDemoSubjects do
  @moduledoc """
  RFC section 5 example domain (Ingress-and-Settlement) workload MFAs.

  Both subjects implement the SAME per-op contract (accept one inbound
  work order, settle it) under two allocation profiles:

  * `status_quo_subject/1` — per-op: map-built ticket records (nested
    map copies with churn), queue-list append, integer-minor-unit
    decimal currency math with accumulator churn. Real allocations.
  * `pack_subject/1` — per-op: zero-GC-at-ops-scale byte-walk ticket
    ingest (BEAM subject; "zero-alloc" is reserved for the
    `:rust_no_std` target)
    (`:binary.at/2` scan of the work-order payload — integers only, no
    heap terms built) plus a settlement counter threaded through the
    loop. Same byte-walk pattern as R6's CscbStatusQuo.run_pack/2
    (falsifier-proven: constant GC delta from 2k → 200k ops; the
    earlier <<>>-encode + ring-put_elem form measured LOW-alloc, not
    zero — per-op heap binaries + tuple copies — and was retired).

  Downstream numbers are MEASURED on this machine only. The RFC's
  section 5 table is ILLUSTRATIVE and is never copied here. Currency
  math uses integer minor units with explicit rounding (no Decimal dep
  exists at this repo root; disclosed in the lane receipt).
  """
  # ── Subject builders ──────────────────────────────────────────────

  @doc "Status-quo domain MFA (see run_status_quo/4)."
  def status_quo_subject(opts \\ []) when is_list(opts) do
    ops = Keyword.get(opts, :ops, 2_000)
    payload_bytes = Keyword.get(opts, :payload_bytes, 256)
    fee_bp = Keyword.get(opts, :fee_bp, 30)
    latency_us = Keyword.get(opts, :latency_us, 20)
    {__MODULE__, :run_status_quo, [ops, payload_bytes, fee_bp, latency_us]}
  end

  @doc "Pack domain MFA (see run_pack/3)."
  def pack_subject(opts \\ []) when is_list(opts) do
    ops = Keyword.get(opts, :ops, 2_000)
    payload_bytes = Keyword.get(opts, :payload_bytes, 256)
    fee_bp = Keyword.get(opts, :fee_bp, 30)
    {__MODULE__, :run_pack, [ops, payload_bytes, fee_bp]}
  end

  # ── Status-quo workload body ──────────────────────────────────────

  @doc false
  def run_status_quo(ops, payload_bytes, fee_bp, latency_us) do
    payload = :binary.copy(<<"wo">>, div(payload_bytes, 2))

    for _ <- 1..ops do
      # 1. map-built ticket record (nested copies, churn)
      ticket =
        %{}
        |> Map.put(:id, payload)
        |> Map.put(:status, :ingress)
        |> Map.put(:amount_minor, 12_345)
        |> Map.put(:fee_bp, fee_bp)

      ticket = Map.put(ticket, :settled_amount, settle(12_345, fee_bp))

      # 2. queue-list append + rebuild (churn)
      _queue = [ticket | build_list(32, [])]

      # 3. decimal currency math on integer minor units w/ accumulator
      _ = settle(999_999, fee_bp)
      _ = settle(777_777, fee_bp)

      # 4. injected latency as real busy-wait CPU (never Process.sleep)
      busy_wait_us(latency_us)
    end

    :ok
  end

  # Integer-minor-unit currency math with explicit banker-free rounding:
  # fee = amount * fee_bp / 10000 rounded to nearest minor unit; then
  # net = amount - fee. Real arithmetic per op, allocates small ints.
  defp settle(amount, fee_bp) do
    fee = div(amount * fee_bp + 5_000, 10_000)
    amount - fee
  end

  defp build_list(0, acc), do: acc
  defp build_list(n, acc), do: build_list(n - 1, [n | acc])

  # ── Pack workload body ────────────────────────────────────────────

  @doc false
  def run_pack(ops, payload_bytes, fee_bp) do
    payload = :binary.copy(<<"wo">>, div(payload_bytes, 2))
    _ = pack_loop(ops, payload, fee_bp, 0)
    :ok
  end

  # Zero-GC-at-ops-scale hot loop (BEAM subject, R6 byte-walk pattern, ingress-settlement
  # semantics): per op the work-order payload is INGESTED via a
  # `:binary.at/2` byte-walk validation scan (integers only — no heap
  # terms built; the naive `<<"wo", rest::binary>>` clause form is NOT
  # allocation-free) and the settlement fee/net math feeds a counter
  # threaded through the loop. Small-int arithmetic (amount, fee, net
  # all immediate-tagged on 64-bit) allocates nothing per op.
  defp pack_loop(0, _payload, _fee_bp, _count), do: :ok

  defp pack_loop(remaining, payload, fee_bp, count) do
    fee = div(12_345 * fee_bp + 5_000, 10_000)
    net = 12_345 - fee
    count1 = ingest_walk(payload, 0, byte_size(payload), count + net - fee)
    pack_loop(remaining - 1, payload, fee_bp, count1)
  end

  defp ingest_walk(bin, pos, size, count) when pos < size do
    count1 =
      if :binary.at(bin, pos) == ?w and pos + 1 < size and :binary.at(bin, pos + 1) == ?o do
        count + 1
      else
        count
      end

    ingest_walk(bin, pos + 2, size, count1)
  end

  defp ingest_walk(_bin, pos, size, count) when pos >= size, do: count

  # ── Shared helpers ────────────────────────────────────────────────

  # Busy-wait spin: real CPU compute, never Process.sleep (no-sleep law).
  defp busy_wait_us(0), do: :ok

  defp busy_wait_us(us) do
    deadline = :erlang.monotonic_time(:microsecond) + us
    do_busy_wait(deadline)
  end

  defp do_busy_wait(deadline) do
    if :erlang.monotonic_time(:microsecond) < deadline do
      do_busy_wait(deadline)
    else
      :ok
    end
  end
end
