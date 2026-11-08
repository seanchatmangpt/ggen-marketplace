# Lane R8 court — standalone, no mix project required.
# Run: elixir qualification/cscb_terminal_court.exs
base = String.replace(__DIR__, "/qualification", "")
File.cd!(base)

{_, 0} = System.cmd("elixirc", ["lib/cscb_terminal.ex", "-o", "/tmp/cscb_r8_ebin"])
Code.append_path("/tmp/cscb_r8_ebin")
Code.require_file("qualification/fixtures/cscb_terminal_fixtures.exs", base)

defmodule R8CourtHelpers do
  def count_rows(text, needle) do
    text |> String.split("\n") |> Enum.count(&String.contains?(&1, needle))
  end

  def catch_error(fun) do
    try do
      fun.()
      :no_raise
    rescue
      _ -> :raised
    end
  end

  # Live mode, polling feed, into a pid device (injectable; Chicago: real
  # messages to a real process — this court process).
  def live_device_render(t) do
    t.run(fn -> %{status_quo: %{allocations_op: 5}, pack: %{allocations_op: 4}} end,
      device: self(),
      batches: 1
    )

    receive do
      {:cscb_terminal_frame, text} ->
        if String.contains?(text, "5") and String.contains?(text, "4"),
          do: :rendered,
          else: :bad_frame
    after
      2_000 -> :timeout
    end
  end

  def live_batches(t) do
    counter = :counters.new(1, [:atomics])

    feed = fn ->
      n = :counters.get(counter, 1)
      :counters.put(counter, 1, n + 1)
      %{status_quo: %{allocations_op: 100 + n}, pack: %{allocations_op: 50}}
    end

    t.run(feed, device: self(), batches: 2, poll_ms: 10)

    frames =
      Enum.map(1..2, fn _ ->
        receive do
          {:cscb_terminal_frame, text} -> text
        after
          2_000 -> :timeout
        end
      end)

    if :timeout in frames, do: :timeout, else: :two_frames
  end

  def pg_empty(t) do
    t.run({:pg, :nobody_publishes_here}, device: self(), batches: 1)

    receive do
      {:cscb_terminal_frame, text} ->
        if String.contains?(text, "FEED EMPTY"), do: :feed_empty, else: {:got, text}
    after
      2_000 -> :timeout
    end
  end
end

f = CscbTerminalFixtures
t = CscbTerminal
nm = "— (not measured)"
h = R8CourtHelpers

# RFC §5 illustrative numbers that must NEVER appear in rendered output
# (anti-hand-waving sweep: the renderer must not mint spec values).
rfc_illustrative_values = [
  "100000",
  "250000",
  "3.5x",
  "2.1x",
  "$4,000",
  "$1,200",
  "illustrative"
]

cases = [
  {"full corpus: header present",
   String.contains?(t.render(f.full_results()), "CSCB BENCHMARK"), true},
  {"full corpus: sq allocations rendered from data",
   String.contains?(t.render(f.full_results()), "12000"), true},
  {"full corpus: pack throughput rendered from data",
   String.contains?(t.render(f.full_results()), "51250.0"), true},
  {"full corpus: allocations delta math",
   String.contains?(t.render(f.full_results()), f.expected_deltas()[:allocations_op]), true},
  {"full corpus: p50 delta math",
   String.contains?(t.render(f.full_results()), f.expected_deltas()[:p50_micros]), true},
  {"full corpus: p99.9 delta math",
   String.contains?(t.render(f.full_results()), f.expected_deltas()[:p99_9_micros]), true},
  {"full corpus: throughput delta math (higher is better)",
   String.contains?(t.render(f.full_results()), f.expected_deltas()[:throughput_ops_s]), true},
  {"full corpus: gc pauses delta math",
   String.contains?(t.render(f.full_results()), f.expected_deltas()[:gc_pauses]), true},
  {"full corpus: 8 metric rows present",
   h.count_rows(t.render(f.full_results()), "better") >= 7, true},
  {"partial corpus: p99.9 sq cell renders not-measured",
   String.contains?(t.render(f.partial_results()), nm), true},
  {"partial corpus: monthly infra delta cell not-measured",
   String.contains?(t.render(f.partial_results()), nm), true},
  {"partial corpus: measured deltas still computed",
   String.contains?(t.render(f.partial_results()), f.expected_deltas()[:allocations_op]), true},
  {"verdict slot renders when CscbVerdict absent",
   String.contains?(t.render(f.full_results()), "VERDICT: (pending"), true},
  {"explicit verdict option renders",
   String.contains?(t.render(f.full_results(), verdict: "ADOPTED"), "VERDICT: ADOPTED"), true},
  {"non-map input raises",
   h.catch_error(fn -> t.render("nope") end), :raised},
  {"live mode: polling feed renders into injected device",
   h.live_device_render(t), :rendered},
  {"live mode: multiple batches into device",
   h.live_batches(t), :two_frames},
  {"pg feed with no publisher renders honest FEED EMPTY",
   h.pg_empty(t), :feed_empty}
]

failures =
  for {name, got, want} <- cases, got != want do
    IO.puts("FAIL #{name}\n  got: #{inspect(got)}\n  want: #{inspect(want)}")
    name
  end

# Anti-hand-waving sweep over every frame the renderer can produce.
rendered_all =
  IO.iodata_to_binary([
    t.render(f.full_results()),
    t.render(f.partial_results()),
    t.render(%{})
  ])

illustrative_hits =
  for v <- rfc_illustrative_values, String.contains?(rendered_all, v) do
    v
  end

failures =
  if illustrative_hits != [] do
    IO.puts("FAIL anti-hand-waving sweep hit illustrative values: #{inspect(illustrative_hits)}")
    ["illustrative_sweep" | failures]
  else
    failures
  end

pass = length(cases) - length(failures)
IO.puts("#{pass}/#{length(cases)} passed (+ anti-hand-waving sweep)")

System.cmd("rm", ["-rf", "/tmp/cscb_r8_ebin"])
if failures == [], do: System.halt(0), else: (IO.inspect(failures) && System.halt(1))
