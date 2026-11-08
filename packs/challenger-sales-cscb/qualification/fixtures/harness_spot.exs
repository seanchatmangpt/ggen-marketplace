# Lane R5 spot fixtures + court — unmocked load-injection measurement engine.
# Court AND spot-check in one executable script (R4 convention, standalone,
# no mix project). Run: elixir qualification/fixtures/harness_spot.exs
base = String.replace(__DIR__, "/qualification/fixtures", "")
File.cd!(base)
File.rm_rf!("/tmp/cscb_r5_ebin")
File.mkdir_p!("/tmp/cscb_r5_ebin")
{_, 0} = System.cmd("elixirc", ["lib/cscb_harness.ex", "-o", "/tmp/cscb_r5_ebin"])
Code.append_path("/tmp/cscb_r5_ebin")
alias CscbHarness

subject = {Enum, :sum, [1..1_000]}

# -- hand-computed percentile corpus (nearest-rank) ------------------------
# sorted samples [10..300 step 10] (n=20): p50 -> idx ceil(0.50*20)=10 -> 100
# p95 -> idx ceil(0.95*20)=19 -> 190; p99 -> idx 20 -> 200; p999 -> idx 20 -> 200
samples = Enum.map(1..20, fn i -> i * 10 end)
want = %{p50: 100, p95: 190, p99: 200, p999: 200}
got = CscbHarness.percentiles(samples)

{"percentile math vs hand-computed n=20", got, want}

cases = [
  {"percentile math vs hand-computed n=20", got, want},
  {"CRC32 known-vector", CscbHarness.crc32([1, 2, 3]), :erlang.crc32(:erlang.term_to_binary([1, 2, 3]))}
]

# -- real bench court -------------------------------------------------------

r =
  CscbHarness.run_bench(subject,
    iterations: 200,
    concurrency: 1,
    burst: true
  )

serial_ok =
  r.percentiles_ns.p50 > 0 and r.ops_per_sec > 0 and
    length(r.durations_ns) == 200 and is_integer(r.crc32) and r.crc32 > 0

cases =
  cases ++
    [
      {"serial: p50>0 ops/sec>0 len==200 crc>0", serial_ok, true},
      {"serial: burst present at 1.5x", r.burst != nil and r.burst.concurrency == 2 and r.burst.iterations == 300, true},
      {"serial: burst has own percentiles",
       r.burst != nil and r.burst.percentiles_ns.p50 > 0 and
         length(r.burst.durations_ns) == 300 and r.burst.crc32 != r.crc32,
       true},
      {"serial: attest floor unavailable", r.attest, :unavailable},
      {"serial: memory counters observed",
       is_integer(r.memory.processes_delta_bytes) and is_integer(r.memory.worker_heap_delta_bytes), true},
      {"serial: reductions observed", is_integer(r.reductions) and r.reductions > 0, true}
    ]

# CRC stability: two benches of an identical subject produce a stable CRC
# (same number of samples of same-shaped durations -> same term shape? No:
# durations differ per run). Lawful stability claim: CRC is a pure function
# of the raw list — same input list => same CRC (purity, not run equality).
d1 = [5, 7, 9]
d2 = [5, 7, 9]
d3 = [5, 8, 9]

cases =
  cases ++
    [
      {"CRC pure: identical lists equal", CscbHarness.crc32(d1) == CscbHarness.crc32(d2), true},
      {"CRC discriminates: one-sample change differs", CscbHarness.crc32(d1) != CscbHarness.crc32(d3), true}
    ]

# concurrent + pinning best-effort
rc =
  CscbHarness.run_bench(subject,
    iterations: 300,
    concurrency: 4,
    pinning: true
  )

cases =
  cases ++
    [
      {"concurrent: 300 samples across 4 workers", length(rc.durations_ns) == 300, true},
      {"concurrent: p50>0 ops/sec>0", rc.percentiles_ns.p50 > 0 and rc.ops_per_sec > 0, true},
      {"concurrent: fair split recorded iterations==300", rc.iterations == 300, true},
      {"concurrent: pinning best-effort recorded", is_boolean(rc.pinning_applied), true},
      {"concurrent: reductions summed across workers", rc.reductions > 0, true}
    ]

# hostile input: invalid subject is a typed FunctionClauseError, not silence
hostile =
  try do
    CscbHarness.run_bench("not an mfa")
    :no_raise
  rescue
    FunctionClauseError -> :function_clause
  end

cases = cases ++ [{"hostile subject raises FunctionClauseError", hostile, :function_clause}]

failures =
  for {name, got, want} <- cases, got != want do
    IO.puts("FAIL #{name}\n  got: #{inspect(got)}\n  want: #{inspect(want)}")
    name
  end

pass = length(cases) - length(failures)

sample =
  "R5 sample transcript: subject Enum.sum/1..1000 | serial n=200 " <>
    "p50=#{r.percentiles_ns.p50}ns ops/sec=#{Float.round(r.ops_per_sec, 1)} " <>
    "reductions=#{r.reductions} crc=#{r.crc32} | burst c=2 n=300 " <>
    "p50=#{r.burst.percentiles_ns.p50}ns ops/sec=#{Float.round(r.burst.ops_per_sec, 1)} | " <>
    "concurrent c=4 n=300 p50=#{rc.percentiles_ns.p50}ns ops/sec=#{Float.round(rc.ops_per_sec, 1)} " <>
    "reductions=#{rc.reductions}"

IO.puts(sample)
IO.puts("#{pass}/#{length(cases)} passed")
File.rm_rf!("/tmp/cscb_r5_ebin")
if failures == [], do: System.halt(0), else: IO.inspect(failures) && System.halt(1)
