# Lane R12 qualification fixtures — Article-15 verdict corpus.
# Lane X2: every measured side declares its :target_profile; each side is
# scored against its own target's bounds.
# Synthetic VALUES are court fixtures, not bench claims.
defmodule CscbVerdictFixtures do
  @stamp "attest:v1:sha256:cscb-r12-fixture"

  def stamp, do: @stamp

  # --- Status-quo side (BEAM comparator, honest bounds) -------------------------

  # Legacy stack: 84ms tail, real allocations, computed SLA breach cost.
  def status_quo_violating,
    do: %{
      p99_max_micros: 84_000.0,
      max_allocation_bytes: 4096,
      sla_breach_cost_usd: 1250.0,
      measured: true,
      stamp: @stamp,
      target_profile: :beam_hot_path
    }

  # Legacy stack that happens to pass the BEAM invariants.
  def status_quo_compliant,
    do: %{status_quo_violating() | p99_max_micros: 8_000.0, max_allocation_bytes: 256, sla_breach_cost_usd: 0.0}

  # --- Pack side, rust_no_std: the RFC invariants (100us / 0 alloc) -------------

  # 8.9µs tail, zero-alloc, zero breach — meets the STRICT rust bounds.
  def pack_meeting,
    do: %{
      p99_max_micros: 8.9,
      max_allocation_bytes: 0,
      sla_breach_cost_usd: 0.0,
      measured: true,
      stamp: @stamp,
      target_profile: :rust_no_std
    }

  # Pack side that itself violates an invariant (anti-self-serving probe).
  def pack_violating,
    do: %{pack_meeting() | max_allocation_bytes: 64}

  # Pack side with no measurement — must force INCONCLUSIVE, never REFUSED.
  def pack_unmeasured,
    do: %{pack_meeting() | measured: false}

  # --- Pack side, beam_hot_path: honest comparator bounds -----------------------

  # Meets BEAM bounds (8ms tail, 400B per op) — meets-on-BEAM, NOT a 100us/
  # 0-alloc proof.
  def pack_beam_meeting,
    do: %{
      p99_max_micros: 8_000.0,
      max_allocation_bytes: 400,
      sla_breach_cost_usd: 0.0,
      measured: true,
      stamp: @stamp,
      target_profile: :beam_hot_path
    }

  # The G11 measured BEAM witness: 33.8ms tail / 106,880B per op. Violates
  # even the honest beam bounds — INCONCLUSIVE, not loosened to ADOPTED.
  def pack_beam_g11_witness,
    do: %{pack_beam_meeting() | p99_max_micros: 33_801.9, max_allocation_bytes: 106_880}

  # A measured side that declares no target — typed-comparison gate refuses.
  def pack_no_target,
    do: Map.delete(pack_meeting(), :target_profile)

  # An unknown target atom on a measured side — same refusal.
  def pack_unknown_target,
    do: Map.put(pack_meeting(), :target_profile, :wasm_edge)

  def economics(total_breach_cost_usd \\ 1250.0),
    do: %{total_breach_cost_usd: total_breach_cost_usd}

  def input(status_quo, pack, economics \\ economics()),
    do: %{status_quo: status_quo, pack: pack, economics: economics}
end
