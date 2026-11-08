# Lane R10/G7 court — Challenger arc FSM (RFC §2.1). Standalone, no mix project.
# Run: elixir qualification/arc_court.exs
base = String.replace(__DIR__, "/qualification", "")
File.cd!(base)

decimal_path = "/Users/sac/ash_pplan/_build/dev/lib/decimal/ebin"

{_, 0} =
  System.cmd("elixirc", [
    "lib/cscb_metric_admission.ex",
    "lib/cscb_economics.ex",
    "lib/cscb_arc.ex",
    "-o",
    "/tmp/cscb_r10_ebin",
    "-pa",
    decimal_path
  ])

Code.append_path(decimal_path)
Code.append_path("/tmp/cscb_r10_ebin")
Code.require_file("qualification/cscb_economics_spot.exs", base)
Code.require_file("qualification/arc_fixtures.exs", base)

fixtures = CscbArcFixtures
arcmod = CscbArc

# ---- Happy path: S1 -> S6, each advance validated ----
happy_result =
  with {:ok, a0} <- {:ok, fixtures.new()},
       {:ok, a1} <- arcmod.advance(a0, fixtures.warmer_payload()),
       {:ok, a2} <- arcmod.advance(a1, fixtures.reframe_payload()),
       {:ok, a3} <- arcmod.advance(a2, fixtures.drowning_payload_valid()),
       {:ok, a4} <- arcmod.advance(a3, fixtures.impact_payload_economics_inputs()),
       {:ok, a5} <- arcmod.advance(a4, fixtures.invariants_payload()),
       {:ok, a6} <- arcmod.advance(a5, fixtures.solution_payload()) do
    {:ok, a6}
  end

happy_ok? =
  case happy_result do
    {:ok, arc_done} ->
      arcmod.arc_complete?(arc_done) and
        arcmod.stages() == [
          :s1_warmer,
          :s2_reframe,
          :s3_rational_drowning,
          :s4_emotional_impact,
          :s5_invariants,
          :s6_solution
        ]

    _ ->
      false
  end

{:ok, final_arc} = happy_result
{:ok, bundle} = arcmod.receipt_inputs(final_arc)

bundle_ok? =
  bundle[:complete] == true and
    map_size(bundle[:stages]) == 6 and
    bundle[:stage_order] == arcmod.stages() and
    bundle[:stages].s6_solution == fixtures.solution_payload()

# ---- Premature-advance refusal matrix ----
{:ok, a1} = arcmod.advance(fixtures.new(), fixtures.warmer_payload())
{:ok, a2} = arcmod.advance(a1, fixtures.reframe_payload())
{:ok, a3} = arcmod.advance(a2, fixtures.drowning_payload_valid())
{:ok, a4} = arcmod.advance(a3, fixtures.impact_payload())
{:ok, a5} = arcmod.advance(a4, fixtures.invariants_payload())

skip_s3 =
  case arcmod.advance(a2, fixtures.drowning_payload_insufficient()) do
    {:error, {:stage_incomplete, :s3_rational_drowning, [{:metric_admission, :min_count_violated}]}} ->
      :typed_refusal

    got ->
      got
  end

refusal_cases = [
  {"S1 zero volume refused", arcmod.advance(fixtures.new(), %{volume: 0, sla_targets: ["x"]}),
   {:error, {:stage_incomplete, :s1_warmer, ["volume must be a positive number"]}}},
  {"S1 missing sla_targets refused", arcmod.advance(fixtures.new(), %{volume: 10}),
   {:error, {:stage_incomplete, :s1_warmer, ["sla_targets is required", "sla_targets must be non-empty"]}}},
  {"S2 empty causes refused", arcmod.advance(a1, %{identified_structural_causes: []}),
   {:error, {:stage_incomplete, :s2_reframe, ["identified_structural_causes must be a non-empty list"]}}},
  {"S3 skip attempt (<3 metrics) typed refusal", skip_s3, :typed_refusal},
  {"S3 all-refused metrics typed", arcmod.advance(a2, fixtures.drowning_payload_all_refused()),
   {:error, {:stage_incomplete, :s3_rational_drowning, [{:metric_admission, :min_count_violated}]}}},
  {"S4 zero total refused", arcmod.advance(a3, fixtures.impact_payload_zero()),
   {:error, {:stage_incomplete, :s4_emotional_impact, ["economic_impact total must be positive"]}}},
  {"S4 missing impact refused", arcmod.advance(a3, %{}),
   {:error, {:stage_incomplete, :s4_emotional_impact, ["economic_impact must be a map"]}}},
  {"S4 loss/2 nil metric typed refusal",
   arcmod.advance(a3, fixtures.impact_payload_economics_inputs_nil_metric()),
   {:error, {:stage_incomplete, :s4_emotional_impact, [{:economics, :nil_metric}]}}},
  {"S4 result-shape missing provenance typed refusal",
   arcmod.advance(a3, fixtures.impact_payload_economics_result_missing_provenance()),
   {:error, {:stage_incomplete, :s4_emotional_impact, [{:economics, :missing_provenance}]}}},
  {"S4 result-shape tampered total typed refusal",
   arcmod.advance(a3, fixtures.impact_payload_economics_result_tampered_total()),
   {:error, {:stage_incomplete, :s4_emotional_impact, [{:economics, :total_mismatch}]}}},
  {"S5 invariant false refused", arcmod.advance(a4, fixtures.invariants_payload_false()),
   {:error, {:stage_incomplete, :s5_invariants, ["invariant bounded_state must be true with an evidence ref"]}}},
  {"S5 missing evidence refused", arcmod.advance(a4, fixtures.invariants_payload_missing_evidence()),
   {:error,
    {:stage_incomplete, :s5_invariants,
     ["invariant bounded_state must be true with an evidence ref",
      "invariant attested_trace must be true with an evidence ref"]}}},
  {"S6 unverified install refused", arcmod.advance(a5, fixtures.solution_payload_unverified()),
   {:error, {:stage_incomplete, :s6_solution, ["install_verified must be true"]}}},
  {"S6 empty IRI refused", arcmod.advance(a5, %{pack_iri: "", install_verified: true}),
   {:error, {:stage_incomplete, :s6_solution, ["pack_iri must be a non-empty string"]}}},
  {"receipt on incomplete arc refused", arcmod.receipt_inputs(a2),
   {:error, {:arc_incomplete, :s3_rational_drowning}}}
]

# S4 result-shape (a real CscbEconomics.loss/2 output, RFC sample) advances:
result_shape_advance =
  case arcmod.advance(a3, fixtures.impact_payload_economics_result()) do
    {:ok, _} -> :advanced
    got -> got
  end

failures =
  Enum.reduce(refusal_cases, [], fn {name, got, want}, acc ->
    if got == want do
      acc
    else
      IO.puts("FAIL #{name}\n  got:  #{inspect(got)}\n  want: #{inspect(want)}")
      [name | acc]
    end
  end)

failures =
  if happy_ok? == true and bundle_ok? == true do
    failures
  else
    IO.puts("FAIL happy=#{inspect(happy_result)} bundle=#{inspect(Map.get(bundle, :stages, :err))}")
    [:happy_or_bundle | failures]
  end

failures =
  if result_shape_advance == :advanced do
    failures
  else
    IO.puts("FAIL S4 result-shape advance: #{inspect(result_shape_advance)}")
    [:s4_result_shape_advance | failures]
  end

# ---- Fallback branch: CscbEconomics NOT loaded (fresh subprocess, no
# economics beam) — legacy total_usd path must stay operative, and a
# loss-input-shaped payload must refuse (nothing to delegate to). ----
fallback_code = """
base = #{inspect(base)}
decimal = #{inspect(decimal_path)}
{_, 0} =
  System.cmd("elixirc", [
    "lib/cscb_metric_admission.ex",
    "lib/cscb_arc.ex",
    "-o",
    "/tmp/cscb_r10_fallback_ebin",
    "-pa",
    decimal
  ])
Code.append_path("/tmp/cscb_r10_fallback_ebin")
Code.require_file("qualification/arc_fixtures.exs", base)
f = CscbArcFixtures
{:ok, a1} = CscbArc.advance(CscbArc.new(f.warmer_payload()), f.warmer_payload())
{:ok, a2} = CscbArc.advance(a1, f.reframe_payload())
{:ok, a3} = CscbArc.advance(a2, f.drowning_payload_valid())
legacy = CscbArc.advance(a3, f.impact_payload())
loss_shaped = CscbArc.advance(a3, f.impact_payload_economics_inputs())
cond do
  elem(legacy, 0) != :ok -> System.halt(3)
  elem(loss_shaped, 0) != :error -> System.halt(4)
  true -> System.halt(0)
end
"""

{fallback_out, 0} = System.cmd("elixir", ["-e", fallback_code])

failures =
  if fallback_out != "" do
    IO.puts("FAIL fallback stdout: #{fallback_out}")
    [:fallback_stdout | failures]
  else
    failures
  end

total = 4 + length(refusal_cases)
pass = total - length(failures)
IO.puts("#{pass}/#{total} passed")

System.cmd("rm", ["-rf", "/tmp/cscb_r10_ebin", "/tmp/cscb_r10_fallback_ebin"])
if failures == [], do: System.halt(0), else: IO.inspect(Enum.reverse(failures)) && System.halt(1)
