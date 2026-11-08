defmodule CscbHardware do
  @moduledoc """
  BEAM-native hardware profile introspection (RFC §2.2).

  Attests the machine itself via `:erlang.system_info/1` — CPU topology,
  logical processor count, OTP/Elixir versions, OS, hostname, and BEAM
  allocator memory. No NIF/Rust/RDTSC anywhere: raw cycle-counter reads are
  Phase 2. The profile is BEAM-visible truth only; it cannot see SMM,
  hypervisor scheduling, or DVFS.

  ## Honesty boundary

  This attests the RUN to the MACHINE as the BEAM observes it. It is NOT a
  TPM, not hardware-enclave anchoring, and not tamper-resistant — a
  sufficiently privileged process can lie to `:erlang.system_info/1`'s
  sources. Enclave anchoring is Phase 2/3.
  """
  @typedoc "BEAM-visible hardware/software profile."
  @type profile :: %{
          required(:cpu_count) => pos_integer(),
          required(:cpu_topology) => term(),
          required(:otp_version) => String.t(),
          required(:elixir_version) => String.t(),
          required(:total_memory) => non_neg_integer(),
          required(:os) => term(),
          required(:hostname) => String.t()
        }

  @doc "BEAM-native machine profile (RFC §2.2 field set)."
  @spec profile() :: profile()
  def profile do
    %{
      cpu_count: :erlang.system_info(:logical_processors_available),
      cpu_topology: canonical_topology(:erlang.system_info(:cpu_topology)),
      otp_version: to_string(:erlang.system_info(:otp_release)),
      elixir_version: System.version(),
      total_memory: :erlang.memory(:system),
      os: :os.type() |> inspect(limit: :infinity),
      hostname: hostname()
    }
  end

  @doc """
  SHA-256 over the canonical serialization of `profile`.

  Deterministic per machine for identical maps: keys are sorted, topology
  normalized, `term_to_binary/1` serialized, hashed. Changes when the
  machine's BEAM-visible profile changes.

  `:total_memory` is EXCLUDED from the digest: BEAM allocator system memory
  fluctuates call-to-call (live process churn), so hashing it would make the
  digest non-deterministic on identical hardware. It stays in `profile/0`
  as volatile telemetry.
  """
  @spec profile_digest(profile()) :: String.t()
  def profile_digest(profile \\ profile()) do
    canonical =
      profile
      |> Map.delete(:total_memory)
      |> Enum.sort()
      |> :erlang.term_to_binary()

    :crypto.hash(:sha256, canonical) |> Base.encode16(case: :lower)
  end

  # :cpu_topology nests arbitrarily; flatten to a depth-tagged list so the
  # digest is stable across calls (never depends on inspect truncation).
  defp canonical_topology(topology) when is_list(topology) do
    Enum.map(topology, fn
      {:logical, n} -> {:logical, n}
      {kind, n, children} -> {kind, n, canonical_topology(children)}
      {kind, n} -> {kind, n}
      n when is_integer(n) -> n
    end)
  end

  defp canonical_topology(other), do: other

  defp hostname do
    {:ok, host} = :inet.gethostname()
    to_string(host)
  end
end
