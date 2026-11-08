# Lane R2 court fixtures — standalone, no mix project required.
# Consumed by qualification/cscb_economics_court.exs (see lane receipt).
defmodule CscbEconomicsSpotFixtures do
  @moduledoc false

  @doc "Pricing map that, with rfc_metrics/0, reproduces the RFC sample figure exactly."
  def rfc_pricing do
    %{
      dollars_per_microsecond: "0.0000006",
      annual_request_volume: 10_000_000,
      hosting_months_per_year: 12,
      coordinator_hourly_rate: "150",
      sla_deduction_per_breach: "470",
      breach_periods_per_year: 12
    }
  end

  @doc "Metric deltas that, with rfc_pricing/0, reproduce the RFC sample figure exactly."
  def rfc_metrics do
    %{
      jitter_ms_over_threshold: 50,
      extra_hosting_monthly: "500",
      coordinator_idle_hours: 0,
      sla_deduction_per_breach: "470",
      breach_rate: 3
    }
  end

  @doc "All-zero deltas: the identity boundary is zero loss."
  def zero_metrics do
    %{
      jitter_ms_over_threshold: 0,
      extra_hosting_monthly: 0,
      coordinator_idle_hours: 0,
      sla_deduction_per_breach: 0,
      breach_rate: 0
    }
  end

  @doc "A negative delta is refused typed."
  def negative_metrics do
    %{rfc_metrics() | extra_hosting_monthly: -500.0}
  end

  @doc "A nil metric is refused typed."
  def nil_metrics do
    %{rfc_metrics() | breach_rate: nil}
  end

  @doc "A missing pricing key is refused typed."
  def missing_pricing do
    Map.delete(rfc_pricing(), :coordinator_hourly_rate)
  end

  @doc "A non-positive rate is refused typed in conversions."
  def zero_rate_pricing do
    %{rfc_pricing() | dollars_per_microsecond: "0"}
  end
end
