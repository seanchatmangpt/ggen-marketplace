defmodule CscbTerminal do
  @moduledoc """
  RFC §4.1 artifact 2 — cscb-terminal live split-screen comparison table.

  BEAM-first honest version. Two laws:

    * Anti-hand-waving in the UI: every rendered cell comes from the result
      maps passed in. A metric absent from a result map renders as
      "— (not measured)". No illustrative/spec number is ever minted here.
    * Delta from data: the delta column is computed from the two result maps
      at render time, never asserted.

  Live mode accepts a feed: a zero-arity polling callback returning a
  results map per batch, or `{:pg, topic}` to pull from a stdlib process
  group a future CscbHarness/CscbBroadcaster may publish to. Device is
  injectable for tests.
  """

  @not_measured "— (not measured)"
  @verdict_slot "VERDICT: (pending — CscbVerdict module not landed)"

  # {key, label, lower_is_better?}
  @metrics [
    {:allocations_op, "allocations/op", true},
    {:rss_bytes, "RSS bytes", true},
    {:p50_micros, "p50 (us)", true},
    {:p95_micros, "p95 (us)", true},
    {:p99_9_micros, "p99.9 (us)", true},
    {:gc_pauses, "GC pauses", true},
    {:throughput_ops_s, "throughput (ops/s)", false},
    {:monthly_infra_usd, "monthly infra $", true}
  ]

  @doc "Render the RFC §5-style comparison table as an ANSI string."
  @spec render(%{optional(atom()) => map() | nil}, keyword()) :: String.t()
  def render(results, opts \\ [])

  def render(results, opts) when is_map(results) do
    sq = Map.get(results, :status_quo) || %{}
    pk = Map.get(results, :pack) || %{}
    verdict = verdict_line(Keyword.get(opts, :verdict))

    [
      "\e[1mCSCB BENCHMARK — STATUS QUO vs PACK\e[0m\n",
      row([pad("metric", 18), pad("status quo", 20), pad("cscb pack", 20), pad("delta", 24)]),
      divider(),
      Enum.map(@metrics, &metric_row(&1, sq, pk)),
      divider(),
      verdict,
      "\n"
    ]
    |> IO.iodata_to_binary()
  end

  def render(_other, _opts), do: raise(ArgumentError, "expected %{status_quo: _, pack: _}")

  @doc """
  Live mode. `feed` is a zero-arity fun returning a results map per batch,
  or `{:pg, topic}` — render whatever a broadcaster publishes to the stdlib
  process group `{:cscb, topic}` (honest empty render when no publisher).
  """
  @spec run(fun() | {:pg, atom() | tuple()}, keyword()) :: :ok
  def run(feed, opts \\ [])

  def run(feed, opts) when is_function(feed, 0) do
    device = Keyword.get(opts, :device, :stdio)
    batches = Keyword.get(opts, :batches, 1)
    poll_ms = Keyword.get(opts, :poll_ms, 250)

    Enum.each(1..batches, fn _ ->
      emit(device, render(feed.(), opts))
      if batches > 1, do: Process.sleep(poll_ms)
    end)

    :ok
  end

  def run({:pg, topic}, opts) do
    group = {:cscb, topic}

    case :pg.get_local_members(group) do
      [] ->
        emit(device(opts),
          render(%{},
            verdict: "FEED EMPTY (no publisher on {:cscb, #{inspect(topic)}})"
          )
        )

      _members ->
        # Broadcaster contract: latest results arrive as messages
        # {:cscb_results, results_map}. Render each received batch.
        batches = Keyword.get(opts, :batches, 1)
        pg_render_loop(batches, opts)
    end
  end

  def run(_other, _opts), do: raise(ArgumentError, "feed must be a fun or {:pg, topic}")

  defp pg_render_loop(0, _opts), do: :ok

  defp pg_render_loop(n, opts) do
    receive do
      {:cscb_results, results} when is_map(results) ->
        emit(device(opts), render(results, opts))
        pg_render_loop(n - 1, opts)
    after
      Keyword.get(opts, :pg_timeout_ms, 500) ->
        emit(device(opts),
          render(%{}, verdict: "FEED TIMEOUT (no batch within #{Keyword.get(opts, :pg_timeout_ms, 500)}ms)")
        )
    end
  end

  defp device(opts), do: Keyword.get(opts, :device, :stdio)

  defp emit(:stdio, text), do: IO.write(text)
  defp emit(pid, text) when is_pid(pid), do: send(pid, {:cscb_terminal_frame, text})
  defp emit(dev, text), do: IO.write(dev, text)

  defp verdict_line(nil) do
    if Code.ensure_loaded?(CscbVerdict) and function_exported?(CscbVerdict, :render, 1) do
      "VERDICT: " <> apply(CscbVerdict, :render, [empty_results()])
    else
      @verdict_slot
    end
  end

  defp verdict_line(v) when is_binary(v), do: "VERDICT: " <> v

  defp metric_row({key, label, lower_is_better?}, sq, pk) do
    sq_v = Map.get(sq, key)
    pk_v = Map.get(pk, key)

    row([
      pad(label, 18),
      pad(cell(sq_v), 20),
      pad(cell(pk_v), 20),
      pad(delta(sq_v, pk_v, lower_is_better?), 24)
    ])
  end

  defp cell(nil), do: @not_measured
  defp cell(v), do: format_number(v)

  defp format_number(v) when is_integer(v), do: Integer.to_string(v)
  defp format_number(v) when is_float(v), do: :erlang.float_to_binary(v, decimals: 1)
  defp format_number(other), do: inspect(other)

  defp delta(nil, _pk, _), do: @not_measured
  defp delta(_sq, nil, _), do: @not_measured
  defp delta(sq, pk, _lower_is_better?) when sq == 0 and pk == 0, do: "no change"
  defp delta(0, _pk, _lower_is_better?), do: "n/a (status quo is 0)"

  defp delta(sq, pk, lower_is_better?) when is_number(sq) and sq != 0 and is_number(pk) do
    pct = (pk - sq) / (sq * 1.0) * 100.0
    better? = if lower_is_better?, do: pct < 0, else: pct > 0
    sign = if pct >= 0, do: "+", else: ""
    dir = if better?, do: "better", else: "worse"
    sign <> format_float(pct) <> "% " <> dir
  end

  defp delta(_sq, _pk, _), do: @not_measured

  defp format_float(f), do: :erlang.float_to_binary(f, decimals: 1)

  defp row(cells), do: Enum.join(cells, "") <> "\n"

  defp pad(s, w) when is_binary(s) do
    if String.length(s) <= w, do: String.pad_trailing(s, w), else: String.slice(s, 0, w)
  end

  defp pad(other, w), do: String.slice(inspect(other), 0, w)

  defp divider, do: String.duplicate("─", 82) <> "\n"

  defp empty_results, do: %{status_quo: nil, pack: nil}
end
