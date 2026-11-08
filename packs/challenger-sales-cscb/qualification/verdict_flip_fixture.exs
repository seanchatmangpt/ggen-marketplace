# Lane AR1 fixture — self-attested sides for verdict-composition attacks.
# The stamps here are genuinely valid per CscbAttest.verify_stamp/1 (the
# header is recomputed on the live machine) — that is the point: even a
# *valid* attestation cannot rescue unattested ECONOMICS.
defmodule CscbAr1Fixture do
  @moduledoc false

  alias CscbAttest, as: A
  alias CscbHardware, as: H

  def status_quo do
    %{
      p99_max_micros: 84_000.0,
      max_allocation_bytes: 4096,
      sla_breach_cost_usd: 1250.0,
      measured: true,
      stamp: self_stamp()
    }
  end

  def pack do
    %{
      p99_max_micros: 8.9,
      max_allocation_bytes: 0,
      sla_breach_cost_usd: 0.0,
      measured: true,
      stamp: self_stamp()
    }
  end

  # A header recomputed on the live machine: passes verify_stamp/1 by
  # construction, since verification recomputes profile_digest/0 and
  # compares it against the attacker-supplied header.
  def self_stamp do
    nonce = A.nonce()
    t = System.monotonic_time()

    %{
      start_time: t,
      end_time: t + 100,
      durations: [50, 50],
      nonce: nonce,
      header: %{profile_digest: H.profile_digest(), nonce: nonce, monotonic_start: t}
    }
  end
end
