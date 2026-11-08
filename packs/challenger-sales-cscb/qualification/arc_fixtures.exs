# Lane R10 qualification fixtures — Challenger arc corpus (RFC §2.1).
defmodule CscbArcFixtures do
  @stamp "attest:v1:sha256:cscb-r10-fixture"

  def warmer_payload,
    do: %{volume: 5_000, sla_targets: ["p99 <= 100us", "zero alloc hot path"]}

  def reframe_payload,
    do: %{identified_structural_causes: ["per-request ETS scan", "unbounded mailbox drain"]}

  def metric(impacts \\ ["EI-1"]) do
    %{
      p99_max_micros: 95.0,
      max_allocation_bytes: 0,
      measured: true,
      stamp: @stamp,
      impacts: impacts
    }
  end

  def tail_inflated_metric do
    %{metric() | p99_max_micros: 140.0}
  end

  def drowning_payload_valid,
    do: %{metrics: [metric(["EI-1"]), metric(["EI-2"]), metric(["EI-1", "EI-3"])]}

  def drowning_payload_insufficient,
    do: %{metrics: [metric(["EI-1"]), metric(["EI-2"])]}

  def drowning_payload_all_refused,
    do: %{metrics: [tail_inflated_metric(), tail_inflated_metric(), tail_inflated_metric()]}

  def impact_payload,
    do: %{economic_impact: %{total_usd: 1_240_000, drivers: ["p99 breach credits", "churn risk"]}}

  def impact_payload_zero, do: %{economic_impact: %{total_usd: 0}}

  # -- CscbEconomics-delegation payloads (RFC sample figures) --------------

  @rfc_metrics %{
    jitter_ms_over_threshold: 50,
    extra_hosting_monthly: "500",
    coordinator_idle_hours: 0,
    sla_deduction_per_breach: "470",
    breach_rate: 3
  }

  @rfc_pricing %{
    dollars_per_microsecond: "0.0000006",
    annual_request_volume: 10_000_000,
    hosting_months_per_year: 12,
    coordinator_hourly_rate: "150",
    sla_deduction_per_breach: "470",
    breach_periods_per_year: 12
  }

  @doc "S4 payload carrying loss/2 INPUTS (metrics + pricing) — delegated path."
  def impact_payload_economics_inputs,
    do: %{economic_impact: %{metrics: @rfc_metrics, pricing: @rfc_pricing}}

  @doc "Delegated path with a nil metric — typed {:economics, :nil_metric} refusal."
  def impact_payload_economics_inputs_nil_metric do
    payload = impact_payload_economics_inputs()
    metrics = Map.put(payload.economic_impact.metrics, :breach_rate, nil)
    %{payload | economic_impact: %{payload.economic_impact | metrics: metrics}}
  end

  @doc "S4 payload carrying a real CscbEconomics.loss/2 OUTPUT (RFC sample: 322,920/yr)."
  def impact_payload_economics_result do
    {:ok, result} = CscbEconomics.loss(@rfc_metrics, @rfc_pricing)
    %{economic_impact: result}
  end

  @doc "loss/2 output with one line's formula provenance stripped."
  def impact_payload_economics_result_missing_provenance do
    {:ok, result} = CscbEconomics.loss(@rfc_metrics, @rfc_pricing)
    stripped = List.update_at(result.lines, 0, &Map.delete(&1, :formula))
    %{economic_impact: %{result | lines: stripped}}
  end

  @doc "loss/2 output with a tampered (non-recomputable) carried total."
  def impact_payload_economics_result_tampered_total do
    {:ok, result} = CscbEconomics.loss(@rfc_metrics, @rfc_pricing)
    %{economic_impact: %{result | total_annual_hemorrhage: Decimal.new(1_000_000)}}
  end

  def invariants_payload do
    %{
      invariants: %{zero_alloc: true, bounded_state: true, attested_trace: true},
      evidence: %{
        zero_alloc: "benchee:alloc:0-bytes-hotpath",
        bounded_state: "state-size:cap-64-slots",
        attested_trace: "attest:v1:sha256:cscb-run-42"
      }
    }
  end

  def invariants_payload_missing_evidence do
    %{invariants_payload() | evidence: %{zero_alloc: "benchee:alloc:0-bytes-hotpath"}}
  end

  def invariants_payload_false do
    put_in(invariants_payload().invariants.bounded_state, false)
  end

  def solution_payload, do: %{pack_iri: "urn:ggen:pack:challenger-sales-cscb", install_verified: true}

  def solution_payload_unverified do
    %{solution_payload() | install_verified: false}
  end

  def new, do: CscbArc.new(warmer_payload())
end
