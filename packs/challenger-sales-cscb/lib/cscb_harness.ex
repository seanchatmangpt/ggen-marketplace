defmodule CscbHarness do
  @moduledoc """
  Unmocked load-injection measurement engine (RFC-2026-0042 Phase 2, BEAM-native).

  Runs a real MFA for real — no mocks, no stubs. The subject `{module, fun, args}`
  is invoked through `apply/3` exactly as written; the harness measures what the
  BEAM actually does.

  Measurements (all durations via `:erlang.monotonic_time(:nanosecond)`):

    * per-op durations -> p50/p95/p99/p999 percentiles
    * throughput ops/sec (iterations / elapsed wall time)
    * memory: `:erlang.memory(:processes)` before/after delta, plus summed
      worker heap-usage deltas read inside each worker via
      `:erlang.process_info(pid, :memory)`
    * reductions: summed from each worker's own final
      `:erlang.process_info(self(), :reductions)` read inside the worker
      (a process cannot read its own counters after exit)

  Scheduler pinning (`pinning: true`) is best-effort: it sets the scheduler
  binding process flag on workers when the running OTP supports it. Pinning
  constrains placement but does NOT guarantee exclusivity — other processes on
  the same scheduler still contend; treat pinned numbers as placement-controlled,
  not isolated. Unsupported emulators skip it (recorded as `pinning_applied: false`).

  Burst mode (`burst: true`): after the nominal phase, a surge phase runs the
  same subject at 1.5x the nominal concurrency and 1.5x the nominal iteration
  count (RFC stage 3 ramp), with its own independent percentile capture,
  ops/sec, memory deltas, and CRC.

  Attestation: if an optional `CscbAttest` module exporting `stamp_result/1`
  is loadable, the result struct is stamped through it; otherwise the struct
  carries `stamp: nil` with `attest: :unavailable` (presence floor, SHACL
  minCount parity with `CscbMetricAdmission`).

  Integrity: CRC32 of the raw duration list — `:erlang.crc32/1` over
  `:erlang.term_to_binary/1` — so consumers can verify the raw samples that
  produced the percentiles.
  """

  defmodule Results do
    @moduledoc """
    Measured values for one bench run. Every field is observed, never claimed:
    `durations_ns` is the raw CRC-anchored sample list, percentiles derive from
    it, and memory/reductions are BEAM counters read at the named points.
    """

    @enforce_keys [
      :subject,
      :iterations,
      :concurrency,
      :pinning,
      :pinning_applied,
      :durations_ns,
      :percentiles_ns,
      :total_ns,
      :ops_per_sec,
      :memory,
      :reductions,
      :crc32,
      :stamp,
      :attest,
      :burst
    ]

    defstruct @enforce_keys

    @type percentile_map :: %{p50: number(), p95: number(), p99: number(), p999: number()}

    @type memory_map :: %{
            processes_before: non_neg_integer(),
            processes_after: non_neg_integer(),
            processes_delta_bytes: integer(),
            worker_heap_before: non_neg_integer(),
            worker_heap_after: non_neg_integer(),
            worker_heap_delta_bytes: integer()
          }

    @type t :: %__MODULE__{
            subject: {module(), atom(), list()},
            iterations: pos_integer(),
            concurrency: pos_integer(),
            pinning: boolean(),
            pinning_applied: boolean(),
            durations_ns: [pos_integer()],
            percentiles_ns: percentile_map(),
            total_ns: pos_integer(),
            ops_per_sec: float(),
            memory: memory_map(),
            reductions: non_neg_integer(),
            crc32: non_neg_integer(),
            stamp: term(),
            attest: :stamped | :unavailable,
            burst: t() | nil
          }
  end

  @doc """
  Bench a real MFA. `subject` is `{module, fun, args}`; opts:

    * `:iterations`  — total ops (default 1_000)
    * `:concurrency` — spawned task workers (default 1)
    * `:pinning`     — best-effort scheduler binding (default false)
    * `:burst`       — append a 1.5x surge phase (default false)

  Returns `%CscbHarness.Results{}`.
  """
  @spec run_bench({module(), atom(), list()}, keyword()) :: Results.t()
  def run_bench({m, f, a} = subject, opts \\ []) when is_atom(m) and is_atom(f) and is_list(a) do
    n = max(1, Keyword.get(opts, :iterations, 1_000))
    c = max(1, Keyword.get(opts, :concurrency, 1))
    pinning = Keyword.get(opts, :pinning, false)

    nominal = run_phase(subject, n, c, pinning)
    burst = if Keyword.get(opts, :burst, false), do: run_burst(subject, n, c, pinning), else: nil

    nominal
    |> struct!(burst: burst)
    |> attest()
  end

  # -- phases ------------------------------------------------------------

  defp run_phase(subject, n, c, pinning) do
    mem_before = :erlang.memory(:processes)

    {durations, total_ns, worker_heap, pinning_applied, reductions} =
      measure_workers(subject, n, c, pinning)

    mem_after = :erlang.memory(:processes)

    ops_per_sec = n / (total_ns / 1.0e9)

    %Results{
      subject: subject,
      iterations: n,
      concurrency: c,
      pinning: pinning,
      pinning_applied: pinning_applied,
      durations_ns: durations,
      percentiles_ns: percentiles(durations),
      total_ns: total_ns,
      ops_per_sec: ops_per_sec,
      memory: %{
        processes_before: mem_before,
        processes_after: mem_after,
        processes_delta_bytes: mem_after - mem_before,
        worker_heap_before: worker_heap.before,
        worker_heap_after: worker_heap.after,
        worker_heap_delta_bytes: worker_heap.after - worker_heap.before
      },
      reductions: reductions,
      crc32: crc32(durations),
      stamp: nil,
      attest: :unavailable,
      burst: nil
    }
  end

  defp run_burst(subject, n, c, pinning) do
    surge_c = max(1, ceil(c * 1.5))
    surge_n = max(1, ceil(n * 1.5))
    run_phase(subject, surge_n, surge_c, pinning)
  end

  # -- workers ------------------------------------------------------------

  # Spawns `c` task workers, each running its fair share of n iterations
  # (workers 1..rem(n, c) take one extra op so the total is exactly n).
  # Each worker reads its own heap usage and final reduction count inside
  # itself and reports them before exit; wall clock spans worker spawn to
  # last-join.
  defp measure_workers(subject, n, c, pinning) do
    parent = self()
    t0 = :erlang.monotonic_time(:nanosecond)

    tasks =
      for worker <- 1..c do
        Task.async(fn ->
          pinning_applied = if pinning, do: best_effort_pin(), else: false
          heap_before = heap_bytes(self())

          per = div(n, c)
          extra = if worker <= rem(n, c), do: 1, else: 0
          durs = do_iterations(subject, per + extra, [])

          heap_after = heap_bytes(self())
          {_, reds} = :erlang.process_info(self(), :reductions)

          send(parent, {:cscb_worker_counters, heap_before, heap_after, reds, pinning_applied})
          durs
        end)
      end

    counters =
      for _ <- 1..c do
        receive do
          {:cscb_worker_counters, hb, ha, reds, pinned} -> {hb, ha, reds, pinned}
        end
      end

    results = Task.await_many(tasks, :infinity)
    t1 = :erlang.monotonic_time(:nanosecond)

    {before_list, after_list, reds_list, pinned_list} = unzip4(counters)

    {
      List.flatten(results),
      t1 - t0,
      %{before: Enum.sum(before_list), after: Enum.sum(after_list)},
      Enum.any?(pinned_list, & &1) and Enum.all?(pinned_list, & &1) and pinning,
      Enum.sum(reds_list)
    }
  end

  defp do_iterations(_subject, 0, durs), do: Enum.reverse(durs)

  defp do_iterations({m, f, a} = subject, count, durs) when count > 0 do
    t0 = :erlang.monotonic_time(:nanosecond)
    apply(m, f, a)
    t1 = :erlang.monotonic_time(:nanosecond)
    do_iterations(subject, count - 1, [t1 - t0 | durs])
  end

  defp unzip4(list) do
    Enum.reduce(Enum.reverse(list), {[], [], [], []}, fn {a, b, c, d}, {as, bs, cs, ds} ->
      {[a | as], [b | bs], [c | cs], [d | ds]}
    end)
  end

  defp heap_bytes(pid) do
    case :erlang.process_info(pid, :memory) do
      {:memory, bytes} when is_integer(bytes) -> bytes
      _ -> 0
    end
  end

  # Best-effort scheduler binding. Returns true only when the emulator
  # accepted the flag; placement is constrained, never exclusive.
  defp best_effort_pin do
    case :erlang.process_flag(:scheduler_binding, true) do
      true -> true
      _ -> false
    end
  rescue
    _ -> false
  end

  # -- stats -------------------------------------------------------------

  @doc """
  Percentiles over the raw duration list. Nearest-rank: index =
  ceil(p/100 * n) into the ascending-sorted samples, clamped to 1..n.
  Verified in the court against a hand-computed corpus.
  """
  @spec percentiles([pos_integer()]) :: Results.percentile_map()
  def percentiles(durations) when is_list(durations) do
    sorted = Enum.sort(durations)
    n = length(sorted)
    %{p50: rank(sorted, n, 50), p95: rank(sorted, n, 95), p99: rank(sorted, n, 99), p999: rank(sorted, n, 99.9)}
  end

  defp rank(sorted, n, p) do
    idx = p * n / 100 |> ceil() |> max(1) |> min(n)
    Enum.at(sorted, idx - 1)
  end

  @doc "CRC32 of the raw duration list: :erlang.crc32 over term_to_binary."
  def crc32(durations) when is_list(durations),
    do: :erlang.crc32(:erlang.term_to_binary(durations))

  # -- attestation ---------------------------------------------------------

  defp attest(%Results{} = r) do
    case attest_module() do
      {mod, fun} ->
        case apply(mod, fun, [r]) do
          {:ok, stamp} -> %Results{r | stamp: stamp, attest: :stamped}
          _ -> %Results{r | attest: :unavailable}
        end

      nil ->
        %Results{r | attest: :unavailable}
    end
  end

  defp attest_module do
    if Code.ensure_loaded?(CscbAttest) and function_exported?(CscbAttest, :stamp_result, 1) do
      {CscbAttest, :stamp_result}
    end
  end
end
