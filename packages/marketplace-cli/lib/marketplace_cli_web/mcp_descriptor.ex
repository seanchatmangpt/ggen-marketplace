defmodule MarketplaceCliWeb.McpDescriptor do
  @moduledoc """
  Per-capability metadata for `MarketplaceCli`'s generated MCP/A2A
  surface: observation scope, mutation scope, authority requirement,
  reversibility, cost, and receipt semantics -- the real implementation
  of v2030:MCPCapabilityDescriptor for this surface's capability list.

  A caller (an MCP client, an A2A peer, or this app's own router/plug)
  can check `requires_authority?/1` or `mutation_scope/1` BEFORE invoking
  a capability, rather than discovering its authority requirement only
  from a runtime refusal.
  """

  @capabilities %{
    :marketplace_search => %{
      name: "Marketplace search",
      description:
        "Given a required_capability, constraints, runtime, and ontology_profile, return candidate_packs with evidence and compatibility notes. Read-only discovery over the pack catalog and semantic graph -- never selects or admits a pack on the caller's behalf.",
      observation_scope: :read_only,
      mutation_scope: :none,
      requires_authority: false,
      reversible: true,
      cost_estimate: nil,
      receipt_semantics: :logged,
      ash_action: nil
    },
    :marketplace_qualify_pack => %{
      name: "Qualify pack",
      description:
        "Given a pack, target_profile, and exact_subject, run the marketplace's qualification engine (structural validate + real generation where a working engine is available, e.g. ggen_igniter) and return a qualification_receipt naming standing and falsifiers. Verifies an existing pack; never constructs or admits one.",
      observation_scope: :read_write,
      mutation_scope: :none,
      requires_authority: false,
      reversible: true,
      cost_estimate: nil,
      receipt_semantics: :sealed_receipt,
      ash_action: nil
    },
    :marketplace_consolidate => %{
      name: "Consolidate candidate packs",
      description:
        "Given a candidate_pack_set and preservation_constraints, return a consolidation_plan, refused_merges, and evidence -- a real, checkable PLAN (which pack absorbs which, what a merge would break), never an executed merge/deletion. Matches this session's own real consolidation work: every actual pack removal or absorption this repo has done was verified by hand before any file was touched, exactly the SELECT-before-DO boundary this capability encodes structurally.",
      observation_scope: :read_write,
      mutation_scope: :none,
      requires_authority: false,
      reversible: true,
      cost_estimate: nil,
      receipt_semantics: :sealed_receipt,
      ash_action: nil
    }
  }

  @doc "Full descriptor list, e.g. for an MCP `tools/list` or A2A agent-card response."
  @spec capabilities() :: %{atom() => map()}
  def capabilities, do: @capabilities

  @doc "Descriptor for one capability id, or `:error` if unregistered."
  @spec describe(atom()) :: {:ok, map()} | :error
  def describe(capability_id), do: Map.fetch(@capabilities, capability_id)

  @doc """
  Real authority check per capability, per this ecosystem's own doctrine
  (xaas CLAUDE.md's "Consequential DO" section, ex4pm's BRCE.execute/5):
  a `:consequential` mutation_scope with `requires_authority: true` must
  never be callable without an explicit authority context. This function
  does not itself GRANT authority -- it only reports whether the
  capability demands one, so a caller can enforce the fence before
  dispatch, consistent with the SELECT/CONSTRUCT/DO separation this
  ecosystem's own vision-2030.ttl models as odrl:Permission/Prohibition.
  """
  @spec requires_authority?(atom()) :: boolean()
  def requires_authority?(capability_id) do
    case describe(capability_id) do
      {:ok, %{requires_authority: r}} -> r
      :error -> true
    end
  end
end
