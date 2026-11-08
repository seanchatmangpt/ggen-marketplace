# Lane R12 court (target-aware as of lane X2) — standalone, no mix project.
# Run: elixir qualification/verdict_court.exs
base = String.replace(__DIR__, "/qualification", "")
File.cd!(base)

File.rm_rf!("/tmp/cscb_r12_ebin")
# One-kernel bounds: the verdict engine reads CscbMetricAdmission.target_bounds/1.
{_, 0} =
  System.cmd("elixirc", [
    "lib/cscb_metric_admission.ex",
    "lib/cscb_verdict.ex",
    "-o",
    "/tmp/cscb_r12_ebin"
  ])

Code.append_path("/tmp/cscb_r12_ebin")
Code.require_file("qualification/verdict_fixtures.exs", base)

fx = CscbVerdictFixtures
vv = CscbVerdict

refused_result = vv.rule(fx.input(fx.status_quo_violating(), fx.pack_meeting()))
adopted_result = vv.rule(fx.input(fx.status_quo_compliant(), fx.pack_meeting()))
inconcl_unmeasured = vv.rule(fx.input(fx.status_quo_violating(), fx.pack_unmeasured()))
no_stamp = vv.rule(fx.input(fx.status_quo_violating(), Map.delete(fx.pack_meeting(), :stamp)))
no_econ = vv.rule(%{fx.input(fx.status_quo_violating(), fx.pack_meeting()) | economics: %{}})
pack_bad = vv.rule(fx.input(fx.status_quo_violating(), fx.pack_violating()))
malformed = vv.rule("nope")
unmeasured_no_stamp =
  vv.rule(%{fx.input(fx.status_quo_violating(), fx.pack_unmeasured()) | economics: %{total_breach_cost_usd: 1250.0}})

# Lane X2 target-aware cases:
beam_meets_beam = vv.rule(fx.input(fx.status_quo_violating(), fx.pack_beam_meeting()))
g11_witness = vv.rule(fx.input(fx.status_quo_violating(), fx.pack_beam_g11_witness()))
no_target = vv.rule(fx.input(fx.status_quo_violating(), fx.pack_no_target()))
unknown_target = vv.rule(fx.input(fx.status_quo_violating(), fx.pack_unknown_target()))

{:verdict, refused_r} = refused_result
{:verdict, adopted_r} = adopted_result
{:verdict, inconcl_r} = inconcl_unmeasured
{:verdict, pack_bad_r} = pack_bad
{:verdict, unmeasured_ns_r} = unmeasured_no_stamp
{:verdict, g11_r} = g11_witness
{:verdict, beam_meets_r} = beam_meets_beam

tail_row = Enum.find(refused_r.invariant_rows, &(&1.invariant == :tail_p99))
adopted_tail_row = Enum.find(adopted_r.invariant_rows, &(&1.invariant == :tail_p99))
g11_tail_row = Enum.find(g11_r.invariant_rows, &(&1.invariant == :tail_p99))
g11_alloc_row = Enum.find(g11_r.invariant_rows, &(&1.invariant == :alloc_per_op))
beam_tail_row = Enum.find(beam_meets_r.invariant_rows, &(&1.invariant == :tail_p99))
beam_alloc_row = Enum.find(beam_meets_r.invariant_rows, &(&1.invariant == :alloc_per_op))

cases = [
  # --- Legacy corpus (sides now declare targets explicitly) ---
  {"refused-path verdict", elem(refused_result, 1).verdict, :status_quo_refused},
  {"refused-path names SQ violations",
   refused_r.violated_by_status_quo |> Enum.sort(),
   [:alloc_per_op, :no_sla_breach_cost, :tail_p99]},
  {"refused-path economics total", refused_r.economics_total_usd, 1250.0},
  {"refused-path pack meets all",
   Enum.all?(refused_r.invariant_rows, &(&1.pack == :meets)), true},
  {"refused-path SQ tail value recorded", tail_row.status_quo_value, 84_000.0},
  {"refused-path SQ tail violates", tail_row.status_quo, :violates},
  {"refused-path SQ tail scored vs BEAM bound", tail_row.status_quo_bound, 10_000.0},
  {"refused-path pack tail scored vs RUST bound", tail_row.pack_bound, 100.0},
  {"refused-path tail margin (pack, rust)", tail_row.margin, 100.0 - 8.9},

  {"adopted-path verdict", elem(adopted_result, 1).verdict, :adopted},
  {"adopted-path no violations/missing",
   {adopted_r.violated_by_status_quo, adopted_r.missing}, {[], []}},
  {"adopted-path pack meets all",
   Enum.all?(adopted_r.invariant_rows, &(&1.pack == :meets)), true},
  {"adopted-path tail margin", adopted_tail_row.margin, 100.0 - 8.9},

  {"inconclusive verdict (unmeasured pack)",
   elem(inconcl_unmeasured, 1).verdict, :inconclusive},
  {"inconclusive missing all pack-side",
   Enum.all?(inconcl_r.missing, &match?({:pack, _}, &1)), true},
  {"inconclusive missing count", length(inconcl_r.missing), 3},

  {"unattested refusal: missing pack stamp", no_stamp, {:refused, :unattested_input}},
  {"unattested refusal: economics not computed", no_econ, {:refused, :unattested_input}},
  {"unmeasured side not stamp-gated (routes to INCONCLUSIVE)",
   unmeasured_no_stamp,
   {:verdict, %{unmeasured_ns_r | verdict: :inconclusive}}},
  {"unmeasured-no-stamp missing count", length(unmeasured_ns_r.missing), 3},

  {"pack violating invariant -> inconclusive (anti-self-serving)",
   elem(pack_bad, 1).verdict, :inconclusive},
  {"pack-violating missing empty", pack_bad_r.missing, []},
  {"pack-violating alloc_per_op row violates",
   Enum.find(pack_bad_r.invariant_rows, &(&1.invariant == :alloc_per_op)).pack, :violates},

  {"malformed input refused typed", malformed, {:refused, :unattested_input}},

  # --- Lane X2: target-aware scoring ---
  {"BEAM-meeting pack vs BEAM-violating SQ: refused (mixed-target, typed)",
   elem(beam_meets_beam, 1).verdict, :status_quo_refused},
  {"BEAM pack tail scored vs beam bound (10_000us)", beam_tail_row.pack_bound, 10_000.0},
  {"BEAM pack alloc scored vs beam bound (512B)", beam_alloc_row.pack_bound, 512},
  {"BEAM pack alloc margin vs beam bound", beam_alloc_row.margin, 512 - 400},
  {"BEAM pack tail meets", beam_tail_row.pack, :meets},
  {"BEAM pack alloc meets", beam_alloc_row.pack, :meets},

  # G11's honest witness: 33.8ms tail / 106,880B violates even beam bounds.
  {"G11 BEAM witness -> INCONCLUSIVE (NOT loosened to ADOPTED)",
   g11_r.verdict, :inconclusive},
  {"G11 witness tail violates beam bound (33_801.9 > 10_000)",
   g11_tail_row.pack, :violates},
  {"G11 witness alloc violates beam bound (106_880 > 512)",
   g11_alloc_row.pack, :violates},
  {"G11 witness rows carry the declared beam target",
   {g11_tail_row.pack_target, g11_alloc_row.pack_target}, {:beam_hot_path, :beam_hot_path}},

  # Typed-comparison gate: a measured side MUST name its target.
  {"measured pack without target refused", no_target, {:refused, :unattested_input}},
  {"measured pack with unknown target refused", unknown_target, {:refused, :unattested_input}}
]

failures =
  for {name, got, want} <- cases, got != want do
    IO.puts("FAIL #{name}\n  got: #{inspect(got)}\n  want: #{inspect(want)}")
    name
  end

pass = length(cases) - length(failures)
IO.puts("#{pass}/#{length(cases)} passed")
File.rm_rf!("/tmp/cscb_r12_ebin")
if failures == [], do: exit(:normal), else: exit({:court_failed, failures})
