# Qualification fixture: one diagnostic tree, hostile path.
# drain_line_replacement WITHOUT camera footage must challenge demanding
# exactly camera_inspection_footage_id; complete telemetry admits; unknown
# claim type refuses typed. Executed by verify.py's elixir-eval stage, which
# compiles the behaviour source (vince.ex) plus the generated module and runs
# these verdicts against a real runtime; this file pins the expected verdicts.
prior = TradeReticle.Plumbing

full = %{
  "camera_inspection_footage_id" => "CAM-42",
  "pipe_diameter_reading" => "4in",
  "depth_reading" => "6ft"
}

partial = %{"pipe_diameter_reading" => "4in", "depth_reading" => "6ft"}

verdicts = [
  prior.prior_verdict("drain_line_replacement", full),
  prior.prior_verdict("drain_line_replacement", partial),
  prior.prior_verdict("deck_recoat", %{})
]

case verdicts do
  [{:admit, _}, {:challenge, ["camera_inspection_footage_id"], _},
   {:refuse, {:unknown_claim_type, "deck_recoat"}}] ->
    IO.puts("DRAIN-SPOT PASS: admit / challenge(camera_inspection_footage_id) / refuse(unknown_claim_type)")

  other ->
    IO.puts("DRAIN-SPOT FAIL: unexpected verdicts #{inspect(other)}")
    System.halt(1)
end
