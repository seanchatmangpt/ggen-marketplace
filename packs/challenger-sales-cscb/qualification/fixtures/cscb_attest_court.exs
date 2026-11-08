#!/usr/bin/env elixir
# Lane R3 court - CscbHardware + CscbAttest (RFC 2.2).
# Run from pack root: elixir qualification/fixtures/cscb_attest_court.exs
# Chicago-style: real BEAM introspection, real stamps, real tampering.

lib = Path.expand("../../lib", __DIR__)

Code.compile_file("cscb_hardware.ex", lib)
Code.compile_file("cscb_attest.ex", lib)

defmodule CscbCourt do
  def run do
    cases = cases()

    results = Enum.map(cases, fn {name, f} -> {name, f.()} end)

    failures =
      for {name, res} <- results, res != true do
        IO.puts("FAIL: " <> name)
        IO.inspect(res, label: "  got")
        name
      end

    if failures == [] do
      IO.puts("CSCB ATTEST COURT: #{Enum.count(cases)} cases, 0 failures - CONFORMANT")
      0
    else
      IO.puts("CSCB ATTEST COURT: VIOLATION")
      1
    end
  end

  defp cases do
    [
      {"profile is real BEAM introspection", fn ->
        p = CscbHardware.profile()
        p.cpu_count > 0 and is_integer(p.total_memory) and p.total_memory > 0 and
          is_binary(p.hostname) and p.hostname != "" and
          is_binary(p.otp_version) and is_binary(p.elixir_version)
      end},
      {"profile digest deterministic across calls", fn ->
        CscbHardware.profile_digest() == CscbHardware.profile_digest()
      end},
      {"digest changes when the profile map changes", fn ->
        p1 = CscbHardware.profile()
        p2 = Map.put(p1, :cpu_count, p1.cpu_count + 1)
        CscbHardware.profile_digest(p1) != CscbHardware.profile_digest(p2)
      end},
      {"nonce is 64 hex chars and unique per call", fn ->
        n1 = CscbAttest.nonce()
        n2 = CscbAttest.nonce()
        Regex.match?(~r/^[0-9a-f]{64}$/, n1) and n1 != n2
      end},
      {"stamp/verify round-trip passes on an honest run", fn ->
        t0 = System.monotonic_time()

        run = %{
          start_time: t0,
          end_time: t0 + 100,
          durations: [40, 60],
          nonce: CscbAttest.nonce()
        }

        CscbAttest.verify_stamp(CscbAttest.stamp_run(run, run.nonce)) == :ok
      end},
      {"tampered nonce refused", fn ->
        t0 = System.monotonic_time()

        base_run = %{
          start_time: t0,
          end_time: t0 + 10,
          durations: [10],
          nonce: CscbAttest.nonce()
        }

        stamped = CscbAttest.stamp_run(base_run, base_run.nonce)
        tampered = put_in(stamped, [:header, :nonce], "00")
        CscbAttest.verify_stamp(tampered) == {:error, :stamp_invalid, :nonce_mismatch}
      end},
      {"tampered profile digest refused", fn ->
        t0 = System.monotonic_time()

        base_run = %{
          headerless_marker: nil,
          start_time: t0,
          end_time: t0 + 10,
          durations: [10],
          nonce: CscbAttest.nonce()
        }

        stamped =
          CscbAttest.stamp_run(Map.delete(base_run, :headerless_marker), base_run.nonce)

        tampered = put_in(stamped, [:header, :profile_digest], "deadbeef")
        CscbAttest.verify_stamp(tampered) == {:error, :stamp_invalid, :profile_mismatch}
      end},
      {"clock rollback refused", fn ->
        t0 = System.monotonic_time()

        base_run = %{
          start_time: t0,
          end_time: t0 - 1,
          durations: [10],
          nonce: CscbAttest.nonce()
        }

        stamped = CscbAttest.stamp_run(base_run, base_run.nonce)
        CscbAttest.verify_stamp(stamped) == {:error, :stamp_invalid, :clock_rollback}
      end},
      {"negative duration refused", fn ->
        t0 = System.monotonic_time()

        base_run = %{
          start_time: t0,
          end_time: t0 + 50,
          durations: [60, -5],
          nonce: CscbAttest.nonce()
        }

        stamped = CscbAttest.stamp_run(base_run, base_run.nonce)
        CscbAttest.verify_stamp(stamped) == {:error, :stamp_invalid, :negative_duration}
      end},
      {"missing header refused", fn ->
        t0 = System.monotonic_time()

        bare = %{
          start_time: t0,
          end_time: t0 + 1,
          durations: [1],
          nonce: CscbAttest.nonce()
        }

        CscbAttest.verify_stamp(bare) == {:error, :stamp_invalid, :missing_header}
      end}
    ]
  end
end

code = CscbCourt.run()
System.halt(code)
