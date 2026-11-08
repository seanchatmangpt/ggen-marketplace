# Lane R4 qualification fixtures — MetricAssertion admission corpus.
# Lane X2: target-aware. Legacy fixtures (no :target_profile) keep the
# conservative rust_no_std default; BEAM fixtures declare beam_hot_path and
# are scored against the honest comparator bounds.
# Synthetic VALUES are court fixtures, not bench claims.
defmodule CscbMetricAdmissionFixtures do
  @stamp "attest:v1:sha256:cscb-r4-fixture"

  # --- Legacy (implicit rust_no_std default) -----------------------------------

  def valid,
    do: %{p99_max_micros: 100.0, max_allocation_bytes: 0, measured: true, stamp: @stamp}

  def valid_at(99.5),
    do: %{p99_max_micros: 99.5, max_allocation_bytes: 0, measured: true, stamp: @stamp}

  def tail_inflation,
    do: %{p99_max_micros: 101.0, max_allocation_bytes: 0, measured: true, stamp: @stamp}

  def allocation_violation,
    do: %{p99_max_micros: 100.0, max_allocation_bytes: 1, measured: true, stamp: @stamp}

  def unmeasured,
    do: %{p99_max_micros: 100.0, max_allocation_bytes: 0, measured: false, stamp: @stamp}

  def missing_stamp,
    do: %{p99_max_micros: 100.0, max_allocation_bytes: 0, measured: true, stamp: nil}

  # --- rust_no_std (explicit) ---------------------------------------------------

  def rust_valid,
    do: Map.put(valid(), :target_profile, :rust_no_std)

  def rust_tail_inflation,
    do: Map.put(tail_inflation(), :target_profile, :rust_no_std)

  # --- beam_hot_path (explicit honest comparator bounds) ------------------------

  # 7.5ms tail / 256B per op: inside beam bounds, admitted as a BEAM comparator.
  def beam_valid,
    do: %{
      p99_max_micros: 7_500.0,
      max_allocation_bytes: 256,
      measured: true,
      stamp: @stamp,
      target_profile: :beam_hot_path
    }

  # At the beam edge: exactly 10_000us and 512B — still admits (<= bounds).
  def beam_at_bounds,
    do: %{
      p99_max_micros: 10_000.0,
      max_allocation_bytes: 512,
      measured: true,
      stamp: @stamp,
      target_profile: :beam_hot_path
    }

  # 10_001us: one microsecond over the beam ceiling — refused.
  def beam_tail_inflation,
    do: %{beam_valid() | p99_max_micros: 10_001.0}

  # 513B: one byte over the beam alloc ceiling — refused.
  def beam_alloc_violation,
    do: %{beam_valid() | max_allocation_bytes: 513}

  # The G11 measured BEAM witness shape (33.8ms tail / 106,880B): refused
  # honestly by beam bounds — never loosened to admit it.
  def beam_g11_witness,
    do: %{beam_valid() | p99_max_micros: 33_801.9, max_allocation_bytes: 106_880}

  # A rust_no_std claim cannot ride the looser beam alloc bounds (p99 kept
  # within the rust tail ceiling so the alloc invariant is the one under test).
  def rust_on_beam_bounds,
    do: %{beam_valid() | p99_max_micros: 50.0, target_profile: :rust_no_std}

  # --- Closed-vocabulary guard ---------------------------------------------------

  def unknown_target,
    do: Map.put(valid(), :target_profile, :wasm_edge)

  # --- Arc helpers ----------------------------------------------------------------

  def metric(impact_ids) when is_list(impact_ids) do
    Map.put(valid(), :impacts, impact_ids)
  end

  def beam_metric(impact_ids) when is_list(impact_ids) do
    Map.put(beam_valid(), :impacts, impact_ids)
  end

  def stage(metrics), do: %{metrics: metrics}
end
