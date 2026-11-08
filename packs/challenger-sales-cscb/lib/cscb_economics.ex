defmodule CscbEconomics do
  @moduledoc """
  EconomicImpact calculator — S4 ("Emotional Impact") stage math
  (RFC-2026-0042 §5.1 stage 4, schema per §1.2).

  Converts metric deltas into an annualized, per-line-item dollar
  hemorrhage using strict `Decimal` arithmetic. Every line item carries
  its own arithmetic provenance (formula string + intermediate values)
  so an auditor can recompute each figure without re-deriving the model.

  Line formulas (annualization factors come from the pricing map, never
  hard-coded inside a line's arithmetic):

    * `jitter`  : `jitter_ms_over_threshold × 1000 → µs` ×
                  `dollars_per_microsecond` × `annual_request_volume`
    * `hosting` : `extra_hosting_monthly × hosting_months_per_year`
    * `idle`    : `coordinator_idle_hours × coordinator_hourly_rate`
    * `sla`     : `sla_deduction_per_breach × breach_rate × breach_periods_per_year`

  The RFC's illustrative sample ("50ms-jitter × SLA deduction + hosting
  = total 322,920/yr per 10k GMV") DOES reproduce exactly under this
  model — see `qualification/cscb_economics_spot.exs` for the
  line-by-line reconciliation.

  Refusal vocabulary (typed, closed, mirroring `CscbMetricAdmission`):

    * `{:refused, :negative_metric}`  — a metric delta below zero
    * `{:refused, :nil_metric}`       — a required metric key missing/nil/non-numeric
    * `{:refused, :invalid_pricing}`  — pricing map key missing/nil/non-numeric
    * `{:refused, :invalid_pricing}`  — pricing value not strictly positive
      (a zero or negative rate cannot inflate/offset a real loss — AR1)
    * `{:refused, :invalid_pricing}`  — a non-positive rate in a conversion
  """

  alias Decimal, as: D

  @required_metrics ~w(jitter_ms_over_threshold extra_hosting_monthly
    coordinator_idle_hours sla_deduction_per_breach breach_rate)a

  @required_pricing ~w(dollars_per_microsecond annual_request_volume
    hosting_months_per_year coordinator_hourly_rate
    sla_deduction_per_breach breach_periods_per_year)a

  @type economic_impact :: %{
          required(:lines) => [line_item()],
          required(:total_annual_hemorrhage) => Decimal.t()
        }

  @type line_item :: %{
          required(:name) => atom(),
          required(:formula) => String.t(),
          required(:inputs) => %{atom() => Decimal.t()},
          required(:annual_amount) => Decimal.t()
        }

  @type refusal ::
          {:refused, :negative_metric | :nil_metric | :invalid_pricing}

  @doc """
  Rate conversion per RFC §1.2: `ms → µs → dollars` (strict Decimal).

  Returns `{:ok, dollars}` or a typed refusal. Zero jitter is lawful and
  yields `{:ok, 0}`; a negative jitter or non-positive rate refuses.
  """
  @spec dollars_per_microsecond(number() | Decimal.t(), number() | Decimal.t()) ::
          {:ok, Decimal.t()} | refusal()
  def dollars_per_microsecond(jitter_ms, rate) do
    with {:ok, ms} <- non_negative(jitter_ms),
         {:ok, r} <- positive(rate) do
      us = D.mult(to_dec(ms), 1000)
      {:ok, D.mult(us, r)}
    end
  end

  @doc """
  Rate conversion per RFC §1.2: allocation bytes → dollars (strict Decimal).
  """
  @spec dollars_per_allocation_byte(number() | Decimal.t(), number() | Decimal.t()) ::
          {:ok, Decimal.t()} | refusal()
  def dollars_per_allocation_byte(bytes, rate) do
    with {:ok, b} <- non_negative(bytes),
         {:ok, r} <- positive(rate) do
      {:ok, D.mult(b, r)}
    end
  end

  @doc """
  Computes the annualized EconomicImpact for S4 stage math.

  Returns `{:ok, %{lines: [line_item], total_annual_hemorrhage: Decimal}}`
  or a typed refusal. Zero deltas in, zero hemorrhage out (identity
  boundary pinned by the spot court).
  """
  @spec loss(map(), map()) :: {:ok, economic_impact()} | refusal()
  def loss(metrics, pricing) when is_map(metrics) and is_map(pricing) do
    with :ok <- check_pricing(pricing),
         :ok <- check_metrics(metrics) do
      j_us = D.mult(to_dec(metrics.jitter_ms_over_threshold), 1000)
      j_rate = to_dec(pricing.dollars_per_microsecond)
      vol = to_dec(pricing.annual_request_volume)

      jitter_line =
        line(:jitter, "jitter_ms × 1000 (µs) × $/µs × annual_request_volume",
             [{:jitter_us, j_us}, {:dollars_per_microsecond, j_rate},
              {:annual_request_volume, vol}],
             D.mult(D.mult(j_us, j_rate), vol))

      host_line =
        line(:hosting, "extra_hosting_monthly × hosting_months_per_year",
             [{:extra_hosting_monthly, to_dec(metrics.extra_hosting_monthly)},
              {:hosting_months_per_year, to_dec(pricing.hosting_months_per_year)}],
             D.mult(to_dec(metrics.extra_hosting_monthly),
                    to_dec(pricing.hosting_months_per_year)))

      idle_line =
        line(:idle, "coordinator_idle_hours × coordinator_hourly_rate",
             [{:coordinator_idle_hours, to_dec(metrics.coordinator_idle_hours)},
              {:coordinator_hourly_rate, to_dec(pricing.coordinator_hourly_rate)}],
             D.mult(to_dec(metrics.coordinator_idle_hours),
                    to_dec(pricing.coordinator_hourly_rate)))

      sla_line =
        line(:sla, "sla_deduction_per_breach × breach_rate × breach_periods_per_year",
             [{:sla_deduction_per_breach, to_dec(pricing.sla_deduction_per_breach)},
              {:breach_rate, to_dec(metrics.breach_rate)},
              {:breach_periods_per_year, to_dec(pricing.breach_periods_per_year)}],
             D.mult(D.mult(to_dec(pricing.sla_deduction_per_breach),
                           to_dec(metrics.breach_rate)),
                    to_dec(pricing.breach_periods_per_year)))

      lines = [jitter_line, host_line, idle_line, sla_line]

      total =
        lines
        |> Enum.map(& &1.annual_amount)
        |> Enum.reduce(D.new(0), &D.add/2)

      {:ok, %{lines: lines, total_annual_hemorrhage: total}}
    end
  end

  def loss(_, _), do: {:refused, :nil_metric}

  # --- provenance-carrying line items -------------------------------------------

  defp line(name, formula, inputs, amount) do
    %{name: name, formula: formula, inputs: Map.new(inputs), annual_amount: amount}
  end

  # --- validation ----------------------------------------------------------------

  defp check_metrics(metrics) do
    Enum.reduce_while(@required_metrics, :ok, fn key, :ok ->
      case Map.fetch(metrics, key) do
        {:ok, nil} ->
          {:halt, {:refused, :nil_metric}}

        {:ok, v} ->
          cond do
            not numeric?(v) -> {:halt, {:refused, :nil_metric}}
            D.compare(to_dec(v), 0) == :lt -> {:halt, {:refused, :negative_metric}}
            true -> {:cont, :ok}
          end

        :error ->
          {:halt, {:refused, :nil_metric}}
      end
    end)
  end

  defp check_pricing(pricing) do
    Enum.reduce_while(@required_pricing, :ok, fn key, :ok ->
      case Map.fetch(pricing, key) do
        {:ok, nil} ->
          {:halt, {:refused, :invalid_pricing}}

        {:ok, v} ->
          cond do
            not numeric?(v) -> {:halt, {:refused, :invalid_pricing}}
            # AR1 (A3/A4): a non-positive pricing entry mints negative
            # offset lines or zeroes a catastrophic loss line. Every
            # pricing key here is positive-domain (rates, volumes,
            # months, hours). Strict positivity, same law as positive/1.
            D.compare(to_dec(v), 0) != :gt -> {:halt, {:refused, :invalid_pricing}}
            true -> {:cont, :ok}
          end

        :error ->
          {:halt, {:refused, :invalid_pricing}}
      end
    end)
  end

  # AR1 (A2): a binary is only numeric if Decimal can actually parse it —
  # numeric?/1 previously accepted "abc" and D.new/1 crashed downstream
  # instead of refusing typed.
  defp numeric?(v) when is_binary(v) do
    match?({%Decimal{}, _rest}, D.parse(v))
  end

  defp numeric?(v) when is_float(v) do
    # Non-finite floats crash D.from_float/1 — refuse typed instead.
    # Guard-free equivalent of is-finite: NaN fails (v == v), infinity
    # exceeds Float.max_finite().
    v == v and abs(v) <= Float.max_finite()
  end

  defp numeric?(v), do: is_number(v) or is_struct(v, Decimal)


  defp non_negative(x) do
    if numeric?(x) do
      d = to_dec(x)

      if D.compare(d, 0) == :lt do
        {:refused, :negative_metric}
      else
        {:ok, d}
      end
    else
      {:refused, :nil_metric}
    end
  end

  defp positive(x) do
    if numeric?(x) do
      d = to_dec(x)

      if D.compare(d, 0) == :gt do
        {:ok, d}
      else
        {:refused, :invalid_pricing}
      end
    else
      {:refused, :invalid_pricing}
    end
  end

  defp to_dec(x) when is_binary(x), do: D.new(x)
  defp to_dec(x) when is_integer(x), do: D.new(x)

  # float in, Decimal out — no float arithmetic downstream of this point
  defp to_dec(x) when is_float(x), do: D.from_float(x)
  defp to_dec(%Decimal{} = d), do: d
end
