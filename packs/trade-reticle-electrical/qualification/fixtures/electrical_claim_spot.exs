# Qualification fixture: one diagnostic tree, hostile path.
# main_breaker_replacement WITHOUT the breaker serial photo must challenge
# demanding exactly breaker_serial_photo; complete telemetry admits; unknown
# claim type refuses typed. Executed by verify.py's elixir-eval stage, which
# compiles the behaviour source (vince.ex) plus the generated module and runs
# these verdicts against a real runtime; this file pins the expected verdicts.
prior = TradeReticle.Electrical

full = %{
  "resistance_readings_log" => "RLOG-118",
  "voltage_log" => "VLOG-118",
  "thermal_image_id" => "TI-118",
  "breaker_serial_photo" => "BSP-118"
}

partial = %{
  "resistance_readings_log" => "RLOG-118",
  "voltage_log" => "VLOG-118",
  "thermal_image_id" => "TI-118"
}

verdicts = [
  prior.prior_verdict("main_breaker_replacement", full),
  prior.prior_verdict("main_breaker_replacement", partial),
  prior.prior_verdict("panel_upgrade", %{})
]

case verdicts do
  [{:admit, _}, {:challenge, ["breaker_serial_photo"], _},
   {:refuse, {:unknown_claim_type, "panel_upgrade"}}] ->
    IO.puts("ELECTRICAL-SPOT PASS: admit / challenge(breaker_serial_photo) / refuse(unknown_claim_type)")

  other ->
    IO.puts("ELECTRICAL-SPOT FAIL: unexpected verdicts #{inspect(other)}")
    System.halt(1)
end
