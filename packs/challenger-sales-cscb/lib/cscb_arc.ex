defmodule CscbArc do
  @moduledoc """
  Six-stage Challenger arc driver (RFC §2.1) as a typed fixed-order FSM.

  The arc is the RFC's forcing function as code: `advance/2` refuses to
  move forward until the current stage's payload validates, so the arc
  literally cannot reach The Solution (S6) without passing Rational
  Drowning (S3: >= 3 admitted metrics) and Emotional Impact (S4: positive
  economic total).

  Stage payloads (typed, per RFC §2.1):

    * S1 `:warmer`             — `volume`, `sla_targets`
    * S2 `:reframe`            — `identified_structural_causes`
    * S3 `:rational_drowning`  — `metrics` (>= 3 admitted; delegates to
      `CscbMetricAdmission.admit_arc/1`)
    * S4 `:emotional_impact`   — `economic_impact`, three lawful shapes:
      (a) `CscbEconomics.loss/2` INPUTS (`metrics` + `pricing` maps) —
      delegated to `CscbEconomics.loss/2` when loadable; (b) a
      `CscbEconomics.loss/2` OUTPUT (`lines` + `total_annual_hemorrhage`) —
      validated by recomputing the total from per-line provenance (the
      carried total is never trusted); (c) legacy inline `total_usd`/`total`
      (fallback when `CscbEconomics` is not loadable).
    * S5 `:invariants`         — envelope `zero_alloc`, `bounded_state`,
      `attested_trace` booleans, each with an evidence ref
    * S6 `:solution`           — `pack_iri` + `install_verified`

  Refusal vocabulary (typed, closed):

    * `{:error, {:stage_incomplete, stage, missing}}` — current stage's
      payload failed validation; `missing` lists the failed fields.
    * `{:error, {:arc_incomplete, stage}}` — receipt bundle requested on
      a non-terminated arc.

  S4 delegation refusals surface as `{:economics, reason}` entries in
  `missing`, with `reason` drawn from `CscbEconomics`' closed refusal
  vocabulary (`:nil_metric`, `:negative_metric`, `:invalid_pricing`)
  plus the delegation-local `:missing_provenance` (a `lines` entry
  without name/formula/inputs/annual_amount) and `:total_mismatch`
  (the carried total disagrees with the recomputed line sum).

  Optional dependencies follow the pack convention: `CscbMetricAdmission`,
  `CscbEconomics`, and `CscbReceipt` are touched only through
  `Code.ensure_loaded?/1` + `function_exported?/3` guards.
  """

  @enforce_keys [:stage, :payloads]
  defstruct [:stage, :payloads]

  @type stage ::
          :s1_warmer
          | :s2_reframe
          | :s3_rational_drowning
          | :s4_emotional_impact
          | :s5_invariants
          | :s6_solution
          | :complete

  @type t :: %__MODULE__{stage: stage(), payloads: %{stage() => map()}}

  @stages [:s1_warmer, :s2_reframe, :s3_rational_drowning, :s4_emotional_impact, :s5_invariants, :s6_solution]

  @doc "Fixed stage order (RFC §2.1)."
  @spec stages() :: [stage()]
  def stages, do: @stages

  @doc """
  Open an arc at S1 (Warmer). `initial` may carry the S1 payload up front;
  `advance/2` still validates it before S2 is reachable.
  """
  @spec new(map()) :: t()
  def new(initial \\ %{}) when is_map(initial) do
    %__MODULE__{stage: :s1_warmer, payloads: %{s1_warmer: initial}}
  end

  @doc """
  Validate the current stage's payload and advance one stage.

  Returns `{:ok, arc}` with the payload stored, or
  `{:error, {:stage_incomplete, stage, missing}}`.
  """
  @spec advance(t(), map()) :: {:ok, t()} | {:error, {:stage_incomplete, stage(), [term()]}}
  def advance(%__MODULE__{stage: stage} = arc, payload) when is_map(payload) do
    case validate(stage, payload) do
      [] -> {:ok, store(arc, stage, payload)}
      missing -> {:error, {:stage_incomplete, stage, missing}}
    end
  end

  defp store(%__MODULE__{payloads: payloads} = arc, :s3_rational_drowning, payload) do
    # AR4 fix (disclosed): store only the ADMITTED metrics, not the raw list.
    # Storing the raw list let refused/unmeasured metrics ride into the
    # receipt bundle alongside the 3 admitted ones (laundering seam feeding
    # the S4-divergence exploit). Gate is unchanged — admission already ran
    # in validate/1 — this only sanitizes what the arc persists.
    clean = sanitize_s3(payload)

    next = next_stage(:s3_rational_drowning)
    %{arc | stage: next, payloads: Map.put(payloads, :s3_rational_drowning, clean)}
  end

  defp store(%__MODULE__{payloads: payloads} = arc, stage, payload) do
    next = next_stage(stage)
    %{arc | stage: next, payloads: Map.put(payloads, stage, payload)}
  end

  defp sanitize_s3(payload) do
    metrics = payload[:metrics]

    admission_loaded? =
      Code.ensure_loaded?(CscbMetricAdmission) and
        function_exported?(CscbMetricAdmission, :admit, 1)

    cond do
      not is_list(metrics) ->
        payload

      admission_loaded? ->
        admitted? = fn m ->
          CscbMetricAdmission.admit(m) == :ok and impact_mapped?(m)
        end

        Map.put(payload, :metrics, Enum.filter(metrics, admitted?))

      true ->
        payload
    end
  end

  defp impact_mapped?(%{impacts: impacts}) when is_list(impacts), do: impacts != []
  defp impact_mapped?(_), do: false

  defp next_stage(:s6_solution), do: :complete
  defp next_stage(stage), do: Enum.at(@stages, Enum.find_index(@stages, &(&1 == stage)) + 1)

  # -- per-stage validators; return the missing/failed list (empty = valid) --

  defp validate(:s1_warmer, payload) do
    missing_presence(payload, volume: "volume", sla_targets: "sla_targets")
    |> Kernel.++(if positive_number?(payload[:volume]), do: [], else: ["volume must be a positive number"])
    |> Kernel.++(if non_empty?(payload[:sla_targets]), do: [], else: ["sla_targets must be non-empty"])
    |> Enum.uniq()
  end

  defp validate(:s2_reframe, payload) do
    if non_empty?(payload[:identified_structural_causes]),
      do: [],
      else: ["identified_structural_causes must be a non-empty list"]
  end

  defp validate(:s3_rational_drowning, payload) do
    metrics = payload[:metrics]

    cond do
      not is_list(metrics) ->
        ["metrics must be a list"]

      Code.ensure_loaded?(CscbMetricAdmission) and
          function_exported?(CscbMetricAdmission, :admit_arc, 1) ->
        case CscbMetricAdmission.admit_arc(%{metrics: metrics}) do
          :ok -> []
          {:refused, reason} -> [{:metric_admission, reason}]
        end

      true ->
        if length(metrics) >= 3, do: [], else: ["metrics requires >= 3 entries"]
    end
  end

  defp validate(:s4_emotional_impact, payload) do
    impact = payload[:economic_impact]

    cond do
      not is_map(impact) ->
        ["economic_impact must be a map"]

      economics_loaded?() and loss_input?(impact) ->
        delegated_loss_check(impact)

      economics_result?(impact) ->
        economics_result_check(impact)

      true ->
        inline_total_check(impact)
    end
  end

  @invariant_keys [:zero_alloc, :bounded_state, :attested_trace]

  defp validate(:s5_invariants, payload) do
    envelope = payload[:invariants]
    evidence = payload[:evidence] || %{}

    if is_map(envelope) do
      for key <- @invariant_keys,
          envelope[key] != true or not non_empty?(evidence[key]),
          do: "invariant #{key} must be true with an evidence ref"
    else
      ["invariants envelope must be a map with #{@invariant_keys |> Enum.join(", ")}"]
    end
  end

  defp validate(:s6_solution, payload) do
    iri_ok = is_binary(payload[:pack_iri]) and payload[:pack_iri] != ""
    verified_ok = payload[:install_verified] == true

    [
      if(iri_ok, do: nil, else: "pack_iri must be a non-empty string"),
      if(verified_ok, do: nil, else: "install_verified must be true")
    ]
    |> Enum.reject(&is_nil/1)
  end

  defp validate(:complete, _payload), do: ["arc already complete"]
  # -- S4 delegation (CscbEconomics, optional dep) ---------------------------

  defp economics_loaded? do
    Code.ensure_loaded?(CscbEconomics) and function_exported?(CscbEconomics, :loss, 2)
  end

  # Shape adapter: S4 payload carries loss/2 INPUTS (metrics + pricing).
  defp loss_input?(%{metrics: metrics, pricing: pricing})
       when is_map(metrics) and is_map(pricing),
       do: true

  defp loss_input?(_), do: false

  # Shape adapter: payload carries a loss/2 OUTPUT verbatim.
  defp economics_result?(%{lines: lines, total_annual_hemorrhage: total}),
    do: is_list(lines) and not is_nil(total)

  defp economics_result?(_), do: false

  defp delegated_loss_check(impact) do
    case CscbEconomics.loss(impact.metrics, impact.pricing) do
      {:ok, result} -> economics_result_check(result)
      {:refused, reason} -> [{:economics, reason}]
    end
  end

  # Validates a CscbEconomics.loss/2 output WITHOUT trusting the carried
  # total: every line must carry its provenance (name, formula, inputs,
  # annual_amount) and the total must equal the recomputed line sum.
  defp economics_result_check(%{lines: lines, total_annual_hemorrhage: total}) do
    provenance_ok? = fn line ->
      is_map(line) and not is_nil(line[:name]) and is_binary(line[:formula]) and
        is_map(line[:inputs]) and numeric?(line[:annual_amount])
    end

    cond do
      Enum.any?(lines, fn line -> not provenance_ok?.(line) end) ->
        [{:economics, :missing_provenance}]

      not numeric?(total) ->
        ["economic_impact total must be positive"]

      true ->
        recomputed =
          Enum.reduce(lines, Decimal.new(0), fn line, acc ->
            Decimal.add(acc, line.annual_amount)
          end)

        cond do
          Decimal.compare(recomputed, total) != :eq ->
            [{:economics, :total_mismatch}]

          Decimal.compare(total, 0) == :gt ->
            []

          true ->
            ["economic_impact total must be positive"]
        end
    end
  end

  defp inline_total_check(impact) do
    total = impact[:total_usd] || impact[:total]

    cond do
      is_nil(total) ->
        ["economic_impact requires a positive total_usd"]

      is_number(total) and total > 0 ->
        []

      true ->
        ["economic_impact total must be positive"]
    end
  end


  # -- completion / receipt --

  @doc "True only when every stage S1..S6 has validated (stage = :complete)."
  @spec arc_complete?(t()) :: boolean()
  def arc_complete?(%__MODULE__{stage: :complete}), do: true
  def arc_complete?(%__MODULE__{}), do: false

  @doc """
  Receipt inputs bundle for `CscbReceipt` (optional dep): all six validated
  payloads plus arc metadata. Refuses a non-terminated arc.
  """
  @spec receipt_inputs(t()) :: {:ok, map()} | {:error, {:arc_incomplete, stage()}}
  def receipt_inputs(%__MODULE__{stage: :complete, payloads: payloads}) do
    {:ok,
     %{
       stages: payloads,
       stage_order: @stages,
       complete: true,
       receipt_target: receipt_target()
     }}
  end

  def receipt_inputs(%__MODULE__{stage: stage}), do: {:error, {:arc_incomplete, stage}}

  defp receipt_target do
    if Code.ensure_loaded?(CscbReceipt) and function_exported?(CscbReceipt, :new, 1),
      do: {:CscbReceipt, :new},
      else: {:map_passthrough, nil}
  end

  # -- helpers --

  defp missing_presence(payload, keys) do
    for {key, _label} <- keys, is_nil(payload[key]), do: "#{key} is required"
  end

  defp positive_number?(n) when is_number(n) and n > 0, do: true
  defp positive_number?(_), do: false

  defp numeric?(n) when is_number(n), do: true
  defp numeric?(%Decimal{}), do: true
  defp numeric?(_), do: false

  defp non_empty?(l) when is_list(l), do: l != []
  defp non_empty?(m) when is_map(m), do: m != %{}
  defp non_empty?(s) when is_binary(s), do: s != ""
  defp non_empty?(_), do: false
end
