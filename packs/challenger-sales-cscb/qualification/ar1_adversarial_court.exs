# Lane AR1 adversarial court — standalone, no mix project required.
# Run: elixir qualification/ar1_adversarial_court.exs
#
# Adversarial review of CscbEconomics.loss/2 + CscbVerdict.rule/1 composed.
# Each attack case prints EXPLOITED or DEFENDED with the actual outcome.

base = String.replace(__DIR__, "/qualification", "")
File.cd!(base)

ebin = "/tmp/cscb_ar1_ebin"
File.rm_rf!(ebin)
File.mkdir_p!(ebin)

{_, 0} =
  System.cmd("elixirc",
    ["lib/cscb_economics.ex", "lib/cscb_verdict.ex", "lib/cscb_attest.ex",
     "lib/cscb_hardware.ex", "-o", ebin,
     "-pa", "/Users/sac/ash_pplan/_build/dev/lib/decimal/ebin"]
  )

Code.append_path("/Users/sac/ash_pplan/_build/dev/lib/decimal/ebin")
Code.append_path(ebin)
Code.require_file("qualification/cscb_economics_spot.exs", base)
Code.require_file("qualification/verdict_flip_fixture.exs", base)

alias CscbEconomicsSpotFixtures, as: F
alias CscbEconomics, as: E
alias CscbVerdict, as: V
alias CscbAr1Fixture, as: X
alias Decimal, as: D

eq = fn a, b -> D.compare(a, D.new(b)) == :eq end

metrics = F.rfc_metrics()
pricing = F.rfc_pricing()

report = fn name, verdict, detail ->
  IO.puts("[#{verdict}] #{name} :: #{detail}")
  {name, verdict}
end

results = []

# ---------------------------------------------------------------------------
# A1. Unit confusion — metrics measured in µs fed into a key named
#     `_ms_`. The formula multiplies by 1000 unconditionally; there is no
#     typed unit field. Does a 1000x inflation slip through silently?
# ---------------------------------------------------------------------------
{us_ratio, base_total} =
  fn ->
    {:ok, base_r} = E.loss(metrics, pricing)
    {:ok, us_r} = E.loss(%{metrics | jitter_ms_over_threshold: 50_000}, pricing)
    {D.to_float(D.div(us_r.total_annual_hemorrhage, base_r.total_annual_hemorrhage)),
     base_r.total_annual_hemorrhage}
  end.()

results = results ++
  [
    report.(
      "A1 unit-confusion (µs fed into _ms_ key)",
      if(abs(us_ratio - 1000.0) < 1.0e-9, do: "EXPLOITED", else: "DEFENDED"),
      "50_000 (µs) in jitter_ms_over_threshold inflates total #{us_ratio}x " <>
        "(base total #{D.to_string(base_total)}); no typed unit field, " <>
        "key name is the only contract"
    )
  ]

# ---------------------------------------------------------------------------
# A2. Float/binary leakage — numeric?/1 accepts ANY binary; a garbage
#     dollar figure ("abc") should be a typed refusal, not a crash.
#     Also: floats are converted via D.from_float (fine) but non-finite
#     floats and unparseable binaries cross the validation gate.
# ---------------------------------------------------------------------------
a2a =
  try do
    E.loss(%{metrics | extra_hosting_monthly: "abc"}, pricing)
  rescue
    e -> {:crashed, e.__struct__, Exception.message(e)}
  end

results = results ++
  [
    report.(
      "A2a garbage binary metric",
      if(match?({:crashed, _, _}, a2a), do: "EXPLOITED", else: "DEFENDED"),
      inspect(a2a)
    )
  ]

a2b =
  try do
    # Real IEEE-754 NaN double, decoded from its bit pattern — both known
    # construction routes; the BEAM validates and refuses both, so a
    # non-finite float cannot reach loss/2 through any Erlang-level path.
    nan = :erlang.binary_to_term(<<131, 70, 127, 248, 0, 0, 0, 0, 0, 0>>)
    E.loss(%{metrics | extra_hosting_monthly: nan}, pricing)
  rescue
    _ ->
      try do
        <<nan::float>> = <<0x7FF8::size(16), 0::size(48)>>
        E.loss(%{metrics | extra_hosting_monthly: nan}, pricing)
      rescue
        e2 -> {:vm_refused, ArgumentError, "VM refuses NaN construction: #{Exception.message(e2)}"}
      end
  end

results = results ++
  [
    report.(
      "A2b non-finite float metric (NaN)",
      if(match?({:crashed, _, _}, a2b), do: "EXPLOITED", else: "DEFENDED"),
      inspect(a2b)
    )
  ]

a2c =
  try do
    E.loss(metrics, %{pricing | coordinator_hourly_rate: "abc"})
  rescue
    e -> {:crashed, e.__struct__, Exception.message(e)}
  end

results = results ++
  [
    report.(
      "A2c garbage binary pricing value",
      if(match?({:crashed, _, _}, a2c), do: "EXPLOITED", else: "DEFENDED"),
      inspect(a2c)
    )
  ]

# ---------------------------------------------------------------------------
# A3. Negative-loss asymmetry — metrics refuse negatives, but PRICING
#     values are only checked numeric?/1. Negative pricing entries produce
#     negative line items that OFFSET a real loss line: the total can net
#     near zero while a genuine hemorrhage line sits inside `lines`.
# ---------------------------------------------------------------------------
{a3_total, a3_neg_lines, a3_outcome} =
  fn ->
    # Real event: 50 ms jitter (line worth $300k), pricing sabotaged so the
    # SLA line is hugely negative and the total nets to ~$4,620.
    sabotaged =
      Map.put(pricing, :sla_deduction_per_breach, "-23542")

    res = E.loss(metrics, sabotaged)

    case res do
      {:ok, r} ->
        neg = Enum.filter(r.lines, fn l -> D.compare(l.annual_amount, 0) == :lt end)
        {D.to_float(r.total_annual_hemorrhage), Enum.map(neg, & &1.name), res}

      refusal ->
        {nil, [], refusal}
    end
  end.()

results = results ++
  [
    report.(
      "A3 negative-pricing offset hides real loss",
      if(a3_total != nil and a3_total < 322_920 / 2, do: "EXPLOITED", else: "DEFENDED"),
      cond do
        a3_total == nil ->
          "sabotaged pricing (sla_deduction_per_breach=-23542) -> " <>
            "#{inspect(a3_outcome)} — refused typed, real loss cannot be offset"

        true ->
          "sabotaged pricing nets total to $#{:erlang.float_to_binary(a3_total * 1.0, decimals: 0)}, " <>
            "gross negative lines present: #{inspect(a3_neg_lines)}, " <>
            "return: #{inspect(elem(a3_outcome, 0))} — loss accepted as {:ok, _}"
      end
    )
  ]

# ---------------------------------------------------------------------------
# A4. Zero-rate pricing — catastrophic jitter (50_000 ms over threshold)
#     with dollars_per_microsecond = 0. The 2-arity helper refuses zero
#     rates (positive/1); loss/2's check_pricing only requires numeric?/1.
# ---------------------------------------------------------------------------
a4 = E.loss(%{metrics | jitter_ms_over_threshold: 50_000}, %{pricing | dollars_per_microsecond: "0"})

a4_jitter_line =
  case a4 do
    {:ok, r} -> r.lines |> Enum.find(&(&1.name == :jitter)) |> Map.fetch!(:annual_amount)
    _ -> nil
  end

results = results ++
  [
    report.(
      "A4 zero-rate pricing zeroes catastrophic loss",
      if(match?({:ok, _}, a4) and a4_jitter_line != nil and eq.(a4_jitter_line, 0),
        do: "EXPLOITED",
        else: "DEFENDED"
      ),
      "catastrophic jitter 50_000 (ms) with $0/µs rate -> " <>
        "#{inspect(a4)}"
    )
  ]

# ---------------------------------------------------------------------------
# A5. Verdict gating — does CscbVerdict validate the ECONOMICS input?
#     economics_computed?/1 accepts any bare number. A fabricated
#     total_breach_cost_usd: 0.0 (never computed by CscbEconomics) feeds
#     the REFUSED rationale as economics_total_usd — a deflated/inflated
#     claim attached to a verdict.
# ---------------------------------------------------------------------------
a5 =
  V.rule(%{
    status_quo: X.status_quo(),
    pack: X.pack(),
    economics: %{total_breach_cost_usd: 0.0}
  })

results = results ++
  [
    report.(
      "A5 fabricated economics feed REFUSED rationale",
      if(match?({:verdict, %{verdict: :status_quo_refused, economics_total_usd: 0.0}}, a5),
        do: "EXPLOITED",
        else: "DEFENDED"
      ),
      "unattested total_breach_cost_usd=0.0 -> #{inspect(a5)}"
    )
  ]

# ---------------------------------------------------------------------------
# A6. Stamp forging — verify_stamp/1 only checks the header against the
#     LIVE machine and internal consistency; an attacker computes
#     profile_digest/0 on their own machine and self-stamps. If the
#     self-stamped side produces :status_quo_refused, the attestation
#     gate adds no adversarial resistance.
# ---------------------------------------------------------------------------
a6 =
  fn ->
    alias CscbAttest, as: A
    alias CscbHardware, as: H

    nonce = A.nonce()
    t = System.monotonic_time()

    forged_sq =
      X.status_quo()
      |> Map.merge(%{
        stamp: %{
          start_time: t,
          end_time: t + 100,
          durations: [50, 50],
          nonce: nonce,
          header: %{profile_digest: H.profile_digest(), nonce: nonce, monotonic_start: t}
        }
      })

    V.rule(%{status_quo: forged_sq, pack: X.pack(), economics: %{total_breach_cost_usd: 1250.0}})
  end.()

results = results ++
  [
    report.(
      "A6 self-forged stamp mints REFUSED verdict",
      if(match?({:verdict, %{verdict: :status_quo_refused}}, a6),
        do: "EXPLOITED",
        else: "DEFENDED"
      ),
      "attacker-supplied header recomputed on own machine -> " <>
        "#{inspect(a6)}"
    )
  ]

# ---------------------------------------------------------------------------
# Court verdict: any EXPLOITED is a finding for the receipt.
# ---------------------------------------------------------------------------
exploited = Enum.count(results, fn {_, v} -> v == "EXPLOITED" end)
defended = Enum.count(results, fn {_, v} -> v == "DEFENDED" end)
IO.puts("ar1 court: #{defended} defended / #{exploited} exploited")

System.at_exit(fn _ ->
  if exploited > 0 do
    IO.puts("ar1 court: findings present (exploited > 0) — exit 1 by design")
    System.stop(1)
  end
end)
