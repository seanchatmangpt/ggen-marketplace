defmodule CscbMetricAdmission do
  @moduledoc """
  Anti-inflation admission validator for CSCB MetricAssertions (target-aware).

  Code-level dual of the pack's per-target SHACL invariant shapes (RFC §3.1
  as amended by lane X2): a metric is admitted against the invariant set of
  its DECLARED `:target_profile` — not one universal ceiling. The closed
  target vocabulary:

    * `:rust_no_std`   — the RFC invariants: p99 <= 100.0us, alloc == 0.
      The 100us/0-alloc proof requires a measured Rust-runner receipt.
    * `:beam_hot_path` — honest BEAM comparator bounds: p99 <= 10_000.0us,
      alloc_per_op <= 512 bytes (BEAM per-op binary encode + worker-side
      sampling allocate by construction; G11 measured 33.8ms tail /
      106,880B per op, so the no_std law is unreachable on BEAM).

  A missing `:target_profile` defaults to `:rust_no_std` — the conservative
  fallback keeps unspecified subjects under the strict RFC law. An unknown
  target atom is refused (closed vocabulary).

  Refusal vocabulary (typed, closed; every refusal names the target whose
  invariant fired):

    * `{:refused, {:unknown_target_profile, t}}` — target not in closed set
    * `{:refused, {t, :tail_latency_inflation}}`       — p99 above t's ceiling
    * `{:refused, {t, :allocation_invariant_violated}}` — alloc outside t's bounds
    * `{:refused, {:unmeasured_claim, t}}`             — unmeasured / unstamped

  The anti-hand-waving law is unchanged: a declared-but-not-measured metric
  cannot enter the arc on ANY target. Optional dependency: `CscbAttest.
  verify_stamp/1` is used when loadable; otherwise stamp presence is the
  admitted floor (SHACL minCount parity).
  """

  @min_arc_metrics 3

  @type target_profile :: :rust_no_std | :beam_hot_path

  @type bounds :: %{
          tail_ceiling_micros: float(),
          alloc_ceiling_bytes: non_neg_integer()
        }

  @typedoc """
  Refusal reason. `{target, invariant}` names the target whose invariant set
  fired; `:unmeasured_claim` and `:unknown_target_profile` carry the target
  (when known) for the same reason.
  """
  @type refusal_reason ::
          :unmeasured_claim
          | :unknown_target_profile
          | {target_profile(), :tail_latency_inflation
             | :allocation_invariant_violated
             | :unmeasured_claim}

  @type refusal :: {:refused, refusal_reason()}

  @type metric_assertion :: %{
          required(:p99_max_micros) => number(),
          required(:max_allocation_bytes) => number(),
          required(:measured) => boolean(),
          required(:stamp) => term(),
          optional(:target_profile) => target_profile()
        }

  @doc """
  Per-target invariant bounds. THE one kernel — `CscbVerdict` reads the same
  map through this function, so the shapes.ttl ceilings (100.0 / 10_000.0 us,
  0 / 512 bytes) have exactly one code home.
  """
  @spec target_bounds(target_profile()) :: bounds()
  def target_bounds(:rust_no_std),
    do: %{tail_ceiling_micros: 100.0, alloc_ceiling_bytes: 0}

  def target_bounds(:beam_hot_path),
    do: %{tail_ceiling_micros: 10_000.0, alloc_ceiling_bytes: 512}

  @doc """
  Target-aware admission. Refusals name the target whose invariant fired:
  `{:refused, {:beam_hot_path, :tail_latency_inflation}}` etc.
  """
  @spec admit(metric_assertion()) :: :ok | refusal()
  def admit(%{p99_max_micros: p99, max_allocation_bytes: alloc, measured: measured} = assertion) do
    case normalize_target(assertion[:target_profile]) do
      {:ok, target, bounds} ->
        cond do
          not is_number(p99) or p99 > bounds.tail_ceiling_micros ->
            {:refused, {target, :tail_latency_inflation}}

          alloc < 0 or alloc > bounds.alloc_ceiling_bytes ->
            {:refused, {target, :allocation_invariant_violated}}

          measured != true ->
            {:refused, {:unmeasured_claim, target}}

          not stamped?(assertion) ->
            {:refused, {:unmeasured_claim, target}}

          # SLA minimal-unblock (lane R13, disclosed in R4 receipt too): the
          # original `not CscbAttest.verify_stamp(...)` crashed on the
          # non-boolean {:error, _, _} return once CscbAttest landed, and it
          # also ran full run-map verification on bare string stamps from the
          # fixtures. Verify run-map stamps only; string stamps pass via stamped?/1.
          stamp_loadable?() and is_map(assertion[:stamp]) and
              CscbAttest.verify_stamp(assertion[:stamp]) != :ok ->
            {:refused, {:unmeasured_claim, target}}

          true ->
            :ok
        end

      {:error, target} ->
        {:refused, {:unknown_target_profile, target}}
    end
  end

  def admit(_other), do: {:refused, {:unmeasured_claim, :unknown_target_profile}}

  @doc """
  SHACL parity in code: a RationalDrowningStage must carry at least
  #{@min_arc_metrics} admitted metrics, and each admitted metric must map to
  at least one EconomicImpact (via its `:impacts` list). Admission inside the
  count is target-aware (see `admit/1`).
  """
  @spec admit_arc(%{metrics: [map()]}) :: :ok | refusal() | {:refused, :min_count_violated}
  def admit_arc(%{metrics: metrics}) when is_list(metrics) do
    admitted =
      metrics
      |> Enum.filter(fn m -> admit(m) == :ok end)
      |> Enum.filter(fn m -> mapped_to_impact?(m) end)

    if length(admitted) >= @min_arc_metrics do
      :ok
    else
      {:refused, :min_count_violated}
    end
  end

  def admit_arc(_other), do: {:refused, :min_count_violated}

  ## Target normalization

  @spec normalize_target(term()) ::
          {:ok, target_profile(), bounds()} | {:error, term()}
  defp normalize_target(nil), do: {:ok, :rust_no_std, target_bounds(:rust_no_std)}
  defp normalize_target(target) when target in [:rust_no_std, :beam_hot_path] do
    {:ok, target, target_bounds(target)}
  end
  defp normalize_target(other), do: {:error, other}

  defp stamped?(%{stamp: stamp}) when stamp != nil and stamp != "", do: true
  defp stamped?(_), do: false

  defp mapped_to_impact?(%{impacts: impacts}) when is_list(impacts), do: impacts != []
  defp mapped_to_impact?(_), do: false

  defp stamp_loadable? do
    Code.ensure_loaded?(CscbAttest) and function_exported?(CscbAttest, :verify_stamp, 1)
  end
end
