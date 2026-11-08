defmodule CscbVerdict do
  @moduledoc """
  Article-15-style verdict engine for a Challenger Sale arc (RFC §5 VERDICT row).

  Consumes a side-by-side comparison — legacy ("status quo") vs pack — plus
  economics and admission proofs, and renders one of three closed verdicts.
  Each side is scored against the invariant set of its own DECLARED
  `:target_profile` (lane X2): the RFC's 100us/0-alloc invariants govern the
  `:rust_no_std` runner target; a `:beam_hot_path` side is scored against
  honest comparator bounds (p99 <= 10_000us, alloc_per_op <= 512B). Bounds
  are read from `CscbMetricAdmission.target_bounds/1` — one kernel, no
  duplicated constants.

  Verdicts (closed vocabulary, unchanged):

    * `:status_quo_refused` — the status quo violates >= 1 invariant of its
      target AND the pack side MEETS its own target's invariants.
    * `:adopted` — the pack meets ALL of its target's invariants with margin
      (regardless of whether the status quo also passes).
    * `:inconclusive` — any required side is unmeasured, or the pack itself
      violates its own target's invariants (anti-self-serving law: the pack
      cannot refuse the legacy stack on violating pack claims).

  Target honesty law (lane X2): a pack declaring `:beam_hot_path` that meets
  beam bounds is scored honestly as meets-on-BEAM — it is NOT adopted as the
  RFC's 100us/0-alloc proof. That proof still requires a measured
  `:rust_no_std` runner receipt. Conversely, an unmeasured rust claim routes
  to INCONCLUSIVE — never to ADOPTED.

  The anti-self-serving law: the pack cannot refuse the legacy stack on
  unmeasured pack claims. An unmeasured pack side forces INCONCLUSIVE with
  an explicit `missing` list — never a refusal of the other side.

  Anti-gaming: a verdict refuses outright (typed `{:refused, :unattested_input}`)
  when a measured side's stamp is missing or fails verification (via the
  optional `CscbAttest.verify_stamp/1` delegate), when a MEASURED side
  declares no (or an unknown) `:target_profile` — the comparison is only
  typed when both measured sides name their target — or when economics are
  not a computed total. Refusal is checked BEFORE any verdict logic runs.
  """

  @type target_profile :: :rust_no_std | :beam_hot_path

  @type side :: %{
          required(:p99_max_micros) => number(),
          required(:max_allocation_bytes) => number(),
          required(:sla_breach_cost_usd) => number(),
          required(:measured) => boolean(),
          optional(:stamp) => term(),
          optional(:target_profile) => target_profile()
        }

  @type input :: %{
          required(:status_quo) => side(),
          required(:pack) => side(),
          required(:economics) => %{required(:total_breach_cost_usd) => number()}
        }

  @type verdict :: :status_quo_refused | :adopted | :inconclusive

  @type invariant_id :: :tail_p99 | :alloc_per_op | :no_sla_breach_cost

  @type invariant_row :: %{
          invariant: invariant_id(),
          status_quo: :meets | :violates | :unmeasured,
          pack: :meets | :violates | :unmeasured,
          status_quo_value: number() | nil,
          pack_value: number() | nil,
          status_quo_target: target_profile() | nil,
          pack_target: target_profile() | nil,
          status_quo_bound: number() | nil,
          pack_bound: number() | nil,
          margin: number() | nil
        }

  @type rationale :: %{
          verdict: verdict(),
          invariant_rows: [invariant_row()],
          economics_total_usd: number(),
          missing: [{:status_quo | :pack, invariant_id()}],
          violated_by_status_quo: [invariant_id()]
        }

  @type refusal :: {:refused, :unattested_input}

  @spec rule(input()) :: {:verdict, rationale()} | refusal()
  def rule(%{status_quo: sq, pack: pack, economics: economics} = _input) do
    with :ok <- target_declared?(sq),
         :ok <- target_declared?(pack),
         :ok <- attested?(sq),
         :ok <- attested?(pack),
         :ok <- economics_computed?(economics) do
      rows = [
        tail_row(sq, pack),
        alloc_row(sq, pack),
        sla_row(sq, pack)
      ]

      missing =
        for row <- rows,
            side <- [:status_quo, :pack],
            Map.fetch!(row, side) == :unmeasured,
            do: {side, row.invariant}

      if missing != [] do
        {:verdict, rationale(:inconclusive, rows, economics, missing, [])}
      else
        sq_violated = for row <- rows, row.status_quo == :violates, do: row.invariant
        pack_all_meet = Enum.all?(rows, fn row -> row.pack == :meets end)

        cond do
          sq_violated != [] and pack_all_meet ->
            {:verdict, rationale(:status_quo_refused, rows, economics, [], sq_violated)}

          pack_all_meet ->
            {:verdict, rationale(:adopted, rows, economics, [], [])}

          true ->
            # Pack itself violates its own target's invariants: the anti-
            # self-serving law forbids refusing the legacy stack on it —
            # INCONCLUSIVE, honestly (G11's BEAM witness lands here).
            {:verdict, rationale(:inconclusive, rows, economics, [], [])}
        end
      end
    end
  end

  def rule(_other), do: {:refused, :unattested_input}

  ## Per-target invariant rows

  # Bounds live in CscbMetricAdmission.target_bounds/1 (one kernel — the
  # shapes.ttl ceilings 100.0/10_000.0us and 0/512B have one code home).
  defp tail_row(sq, pack) do
    per_target_row(:tail_p99, sq, pack, :p99_max_micros,
      meets: fn target, v ->
        v <= CscbMetricAdmission.target_bounds(target).tail_ceiling_micros
      end,
      margin: fn target, v ->
        CscbMetricAdmission.target_bounds(target).tail_ceiling_micros - v
      end,
      bound: fn target -> CscbMetricAdmission.target_bounds(target).tail_ceiling_micros end
    )
  end

  defp alloc_row(sq, pack) do
    per_target_row(:alloc_per_op, sq, pack, :max_allocation_bytes,
      meets: fn target, v ->
        v == 0 or (target == :beam_hot_path and v > 0 and v <= 512)
      end,
      margin: fn
        :rust_no_std, v -> -v
        :beam_hot_path, v -> 512 - v
      end,
      bound: fn target -> CscbMetricAdmission.target_bounds(target).alloc_ceiling_bytes end
    )
  end

  defp sla_row(sq, pack) do
    # Universal invariant: a nonzero SLA breach cost is a breach on every target.
    %{
      invariant: :no_sla_breach_cost,
      status_quo: universal_status(sq, :sla_breach_cost_usd),
      pack: universal_status(pack, :sla_breach_cost_usd),
      status_quo_value: value_if_measured(sq, :sla_breach_cost_usd),
      pack_value: value_if_measured(pack, :sla_breach_cost_usd),
      status_quo_target: declared_target(sq),
      pack_target: declared_target(pack),
      status_quo_bound: 0,
      pack_bound: 0,
      margin: if(measured?(pack), do: -Map.fetch!(pack, :sla_breach_cost_usd), else: nil)
    }
  end

  @spec per_target_row(invariant_id(), side(), side(), atom(), keyword()) :: invariant_row()
  defp per_target_row(invariant, sq, pack, key, opts) do
    meets = Keyword.fetch!(opts, :meets)
    margin = Keyword.fetch!(opts, :margin)
    bound = Keyword.fetch!(opts, :bound)

    sq_target = declared_target(sq)
    pack_target = declared_target(pack)

    %{
      invariant: invariant,
      status_quo: side_status(sq, key, sq_target, meets),
      pack: side_status(pack, key, pack_target, meets),
      status_quo_value: value_if_measured(sq, key),
      pack_value: value_if_measured(pack, key),
      status_quo_target: sq_target,
      pack_target: pack_target,
      status_quo_bound: if(is_target(sq_target), do: bound.(sq_target), else: nil),
      pack_bound: if(is_target(pack_target), do: bound.(pack_target), else: nil),
      margin:
        if(measured?(pack) and is_target(pack_target),
          do: margin.(pack_target, Map.fetch!(pack, key)),
          else: nil
        )
    }
  end

  defp side_status(side, key, target, meets) do
    cond do
      not measured?(side) -> :unmeasured
      not is_target(target) -> :violates
      meets.(target, Map.fetch!(side, key)) -> :meets
      true -> :violates
    end
  end

  defp universal_status(side, key) do
    cond do
      not measured?(side) -> :unmeasured
      Map.fetch!(side, key) == 0 -> :meets
      true -> :violates
    end
  end

  defp rationale(verdict, rows, economics, missing, sq_violated) do
    %{
      verdict: verdict,
      invariant_rows: rows,
      economics_total_usd: economics.total_breach_cost_usd,
      missing: missing,
      violated_by_status_quo: sq_violated
    }
  end

  defp value_if_measured(side, key) do
    if measured?(side), do: Map.fetch!(side, key), else: nil
  end

  defp measured?(%{measured: true}), do: true
  defp measured?(_), do: false

  ## Target declaration gate

  defp declared_target(%{target_profile: t}), do: t
  defp declared_target(_), do: nil

  defp is_target(t), do: t in [:rust_no_std, :beam_hot_path]

  # A MEASURED side with no (or an unknown) declared target is gaming: the
  # comparison is only typed when both measured sides name their target.
  # Unmeasured sides without a target are fine — they route to INCONCLUSIVE.
  defp target_declared?(side) do
    if measured?(side) and not is_target(declared_target(side)) do
      {:refused, :unattested_input}
    else
      :ok
    end
  end

  ## Anti-gaming gates

  defp attested?(side) do
    cond do
      not measured?(side) ->
        # Unmeasured sides route to INCONCLUSIVE, not refusal — but a
        # structurally invalid side (missing stamps on a claimed-measured
        # side) is gaming.
        :ok

      not stamped?(side) ->
        {:refused, :unattested_input}

      # SLA minimal-unblock (lane G11, disclosed in G11 receipt): `not
      # CscbAttest.verify_stamp(...)` raised ArgumentError on the non-boolean
      # :ok / {:error, _, _} returns once CscbAttest landed — same bug class
      # R13 fixed in CscbMetricAdmission. Compare != :ok instead.
      stamp_loadable?() and CscbAttest.verify_stamp(side[:stamp]) != :ok ->
        {:refused, :unattested_input}

      true ->
        :ok
    end
  end

  defp stamped?(%{stamp: stamp}) when stamp != nil and stamp != "", do: true
  defp stamped?(_), do: false

  defp economics_computed?(%{total_breach_cost_usd: total}) when is_number(total) do
    cond do
      # AR1 (A5 partial, re-applied after concurrent-lane overwrite — the
      # restored clause called Float.is_finite/1, which is undefined on this
      # OTP/Elixir build and crashes on ANY float total): guard-safe
      # finiteness. NaN fails (t == t); infinity exceeds Float.max_finite().
      is_float(total) and not (total == total) -> {:refused, :unattested_input}
      is_float(total) and abs(total) > Float.max_finite() -> {:refused, :unattested_input}
      total < 0 -> {:refused, :unattested_input}
      true -> :ok
    end
  end

  defp economics_computed?(_), do: {:refused, :unattested_input}

  defp stamp_loadable? do
    Code.ensure_loaded?(CscbAttest) and function_exported?(CscbAttest, :verify_stamp, 1)
  end
end
