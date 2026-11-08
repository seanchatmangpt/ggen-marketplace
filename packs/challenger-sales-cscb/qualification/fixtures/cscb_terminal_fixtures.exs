# Lane R8 qualification fixtures — CscbTerminal golden-render corpus.
# Two fixed result maps (fully measured and partially unmeasured) plus
# expected delta math, so the court asserts render output without the
# renderer minting a single illustrative number.
defmodule CscbTerminalFixtures do
  @moduledoc false

  # Fully measured status-quo baseline.
  def status_quo do
    %{
      allocations_op: 12_000,
      rss_bytes: 409_600,
      p50_micros: 900.0,
      p95_micros: 1200.0,
      p99_9_micros: 1600.0,
      gc_pauses: 7,
      throughput_ops_s: 41_000.0,
      monthly_infra_usd: 3000
    }
  end

  # Fully measured pack run.
  def pack do
    %{
      allocations_op: 6_000,
      rss_bytes: 204_800,
      p50_micros: 600.0,
      p95_micros: 800.0,
      p99_9_micros: 1100.0,
      gc_pauses: 3,
      throughput_ops_s: 51_250.0,
      monthly_infra_usd: 1500
    }
  end

  # Partially measured status quo: p99.9 and monthly infra unmeasured.
  def partial do
    Map.merge(status_quo(), %{p99_9_micros: nil, monthly_infra_usd: nil})
  end

  def full_results, do: %{status_quo: status_quo(), pack: pack()}
  def partial_results, do: %{status_quo: partial(), pack: pack()}

  # Expected delta strings (computed by hand from the fixtures above;
  # the court asserts the renderer matches, not the other way around).
  def expected_deltas do
    %{
      allocations_op: "-50.0% better",
      rss_bytes: "-50.0% better",
      p50_micros: "-33.3% better",
      p95_micros: "-33.3% better",
      p99_9_micros: "-31.3% better",
      gc_pauses: "-57.1% better",
      throughput_ops_s: "+25.0% better",
      monthly_infra_usd: "-50.0% better"
    }
  end

  # Keys that must render "— (not measured)" in the partial corpus.
  def partial_unmeasured_keys, do: [:p99_9_micros, :monthly_infra_usd]
end
