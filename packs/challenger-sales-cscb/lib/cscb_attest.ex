defmodule CscbAttest do
  @moduledoc """
  Run-to-machine attestation stamps (RFC §2.2).

  Binds a run header — {profile_digest, nonce, monotonic continuity} — into
  a run map and verifies it on replay. Honesty statement (RFC-mandated):

  This attests the RUN to the MACHINE and session, NOT to a TPM. There is
  no hardware-enclave anchoring here; that is Phase 2/3. The stamp proves
  the run claims to have executed on the machine whose BEAM-visible profile
  digest matches, within one monotonic-clock continuity window — nothing
  more.
  """
  alias CscbHardware

  @typedoc "Run header bound by `stamp_run/2`."
  @type header :: %{
          required(:profile_digest) => String.t(),
          required(:nonce) => String.t(),
          required(:monotonic_start) => integer()
        }

  @typedoc "A run: start/end monotonic times, per-step durations, nonce, header."
  @type run :: %{
          required(:start_time) => integer(),
          required(:end_time) => integer(),
          required(:durations) => [integer()],
          required(:nonce) => String.t(),
          optional(:header) => header()
  }

  @doc "Crypto-strong 256-bit nonce, lowercase hex."
  @spec nonce() :: String.t()
  def nonce do
    Base.encode16(:crypto.strong_rand_bytes(32), case: :lower)
  end

  @doc """
  Binds {profile_digest, nonce, monotonic_start} into a run header.

  `monotonic_start` is taken from `run.start_time` (native monotonic units)
  so the header and the run cannot disagree about when the run began.
  """
  @spec stamp_run(run(), String.t()) :: run()
  def stamp_run(%{start_time: t} = run, nonce) when is_integer(t) do
    header = %{
      profile_digest: CscbHardware.profile_digest(),
      nonce: nonce,
      monotonic_start: t
    }

    Map.put(run, :header, header)
  end

  @doc """
  Verifies a stamped run, recomputing every claim from the live machine:

    * recomputed `CscbHardware.profile_digest/0` == `header.profile_digest`
      (else `:profile_mismatch`)
    * `run.nonce == header.nonce` (else `:nonce_mismatch`)
    * `end_time >= monotonic_start` (else `:clock_rollback`)
    * no negative durations (else `:negative_duration`)

  Returns `:ok` or typed
  `{:error, :stamp_invalid, :profile_mismatch | :nonce_mismatch |
  :negative_duration | :clock_rollback}`. A run without a header refuses
  `:missing_header`.
  """
  @spec verify_stamp(run()) :: :ok | {:error, :stamp_invalid, atom()}
  def verify_stamp(%{header: header} = run) when is_map(header) do
    with :ok <- check_profile(header),
         :ok <- check_nonce(header, run),
         :ok <- check_monotonic(run) do
      :ok
    else
      {:error, detail} -> {:error, :stamp_invalid, detail}
    end
  end

  def verify_stamp(_), do: {:error, :stamp_invalid, :missing_header}

  defp check_profile(header) do
    if CscbHardware.profile_digest() == header.profile_digest do
      :ok
    else
      {:error, :profile_mismatch}
    end
  end

  defp check_nonce(header, run) do
    if run.nonce == header.nonce do
      :ok
    else
      {:error, :nonce_mismatch}
    end
  end

  defp check_monotonic(%{end_time: end_time, start_time: start_time} = run) do
    header = run.header

    cond do
      end_time < header.monotonic_start -> {:error, :clock_rollback}
      Enum.any?(run.durations, &(&1 < 0)) -> {:error, :negative_duration}
      end_time < start_time -> {:error, :clock_rollback}
      true -> :ok
    end
  end
end
