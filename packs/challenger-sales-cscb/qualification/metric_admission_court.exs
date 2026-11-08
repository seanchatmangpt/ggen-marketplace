# Lane R4 court (target-aware as of lane X2) — standalone, no mix project.
# Run: elixir qualification/metric_admission_court.exs
base = String.replace(__DIR__, "/qualification", "")
File.cd!(base)

File.rm_rf!("/tmp/cscb_r4_ebin")
{_, 0} = System.cmd("elixirc", ["lib/cscb_metric_admission.ex", "-o", "/tmp/cscb_r4_ebin"])
Code.append_path("/tmp/cscb_r4_ebin")
Code.require_file("qualification/metric_admission_fixtures.exs", base)
alias CscbMetricAdmissionFixtures, as: F
alias CscbMetricAdmission, as: A

cases = [
  # --- Legacy corpus (implicit rust_no_std default; conservative fallback) ---
  {"valid measured admits", A.admit(F.valid()), :ok},
  {"99.5us admits", A.admit(F.valid_at(99.5)), :ok},
  {"101us refused tail", A.admit(F.tail_inflation()),
   {:refused, {:rust_no_std, :tail_latency_inflation}}},
  {"1-byte alloc refused", A.admit(F.allocation_violation()),
   {:refused, {:rust_no_std, :allocation_invariant_violated}}},
  {"unmeasured refused", A.admit(F.unmeasured()), {:refused, {:unmeasured_claim, :rust_no_std}}},
  {"missing stamp refused", A.admit(F.missing_stamp()),
   {:refused, {:unmeasured_claim, :rust_no_std}}},
  {"non-map refused", A.admit("nope"), {:refused, {:unmeasured_claim, :unknown_target_profile}}},

  # --- rust_no_std explicit ---
  {"explicit rust valid admits", A.admit(F.rust_valid()), :ok},
  {"explicit rust 101us refused", A.admit(F.rust_tail_inflation()),
   {:refused, {:rust_no_std, :tail_latency_inflation}}},
  {"rust claim cannot ride beam bounds (256B)",
   A.admit(F.rust_on_beam_bounds()), {:refused, {:rust_no_std, :allocation_invariant_violated}}},

  # --- beam_hot_path honest comparator bounds ---
  {"beam 7.5ms/256B admits", A.admit(F.beam_valid()), :ok},
  {"beam at exact bounds (10000us/512B) admits", A.admit(F.beam_at_bounds()), :ok},
  {"beam 10001us refused tail", A.admit(F.beam_tail_inflation()),
   {:refused, {:beam_hot_path, :tail_latency_inflation}}},
  {"beam 513B refused alloc", A.admit(F.beam_alloc_violation()),
   {:refused, {:beam_hot_path, :allocation_invariant_violated}}},
  {"G11 witness (33.8ms/106880B) refused by BEAM bounds honestly",
   A.admit(F.beam_g11_witness()), {:refused, {:beam_hot_path, :tail_latency_inflation}}},

  # --- Closed target vocabulary ---
  {"unknown target refused", A.admit(F.unknown_target()),
   {:refused, {:unknown_target_profile, :wasm_edge}}},

  # --- Arc-level (target-aware admit inside the count) ---
  {"stage 2 metrics refused minCount",
   A.admit_arc(F.stage([F.metric(["EI-1"]), F.metric(["EI-2"])])), {:refused, :min_count_violated}},
  {"stage 3 rust metrics zero loss-maps refused",
   A.admit_arc(F.stage([F.valid(), F.valid(), F.valid()])), {:refused, :min_count_violated}},
  {"stage 3 rust admitted w/ impacts ok",
   A.admit_arc(F.stage([F.metric(["EI-1"]), F.metric(["EI-2"]), F.metric(["EI-1", "EI-3"])])),
   :ok},
  {"stage 3 beam metrics admitted w/ impacts ok",
   A.admit_arc(F.stage([F.beam_metric(["EI-1"]), F.beam_metric(["EI-2"]),
                        F.beam_metric(["EI-1", "EI-3"])])),
   :ok},
  {"stage: one beam-inflated among 3 falls below minCount",
   A.admit_arc(F.stage([F.beam_metric(["EI-1"]), F.beam_metric(["EI-2"]), F.beam_tail_inflation()])),
   {:refused, :min_count_violated}}
]

failures =
  for {name, got, want} <- cases, got != want do
    IO.puts("FAIL #{name}\n  got: #{inspect(got)}\n  want: #{inspect(want)}")
    name
  end

pass = length(cases) - length(failures)
IO.puts("#{pass}/#{length(cases)} passed")
File.rm_rf!("/tmp/cscb_r4_ebin")
if failures == [], do: System.halt(0), else: IO.inspect(failures) && System.halt(1)
