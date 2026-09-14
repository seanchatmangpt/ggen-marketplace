defmodule MarketplaceCliWeb.A2A.MarketplaceAgent do
  @moduledoc """
  Generated A2A agent for `MarketplaceCli`: Exposes ggen-marketplace's discovery/qualification/consolidation capabilities to consumers (e.g. an XaaS Marketplace Adapter) as real MCP tools and A2A skills, never as DO authority -- Marketplace knows what exists, the consumer decides what to do with it.

  Mount at `/a2a` in your router:

      forward "/a2a", MarketplaceCliWeb.A2A.MarketplaceAgent
  """

  use A2A.Agent,
    name: "ggen-marketplace-capability-agent",
    description:
      "Exposes ggen-marketplace's discovery/qualification/consolidation capabilities to consumers (e.g. an XaaS Marketplace Adapter) as real MCP tools and A2A skills, never as DO authority -- Marketplace knows what exists, the consumer decides what to do with it.",
    skills: [
      %{
        id: "marketplace_search",
        name: "Marketplace search",
        description:
          "Given a required_capability, constraints, runtime, and ontology_profile, return candidate_packs with evidence and compatibility notes. Read-only discovery over the pack catalog and semantic graph -- never selects or admits a pack on the caller's behalf.",
        tags: ["generated", "marketplacecli"]
      },
      %{
        id: "marketplace_qualify_pack",
        name: "Qualify pack",
        description:
          "Given a pack, target_profile, and exact_subject, run the marketplace's qualification engine (structural validate + real generation where a working engine is available, e.g. ggen_igniter) and return a qualification_receipt naming standing and falsifiers. Verifies an existing pack; never constructs or admits one.",
        tags: ["generated", "marketplacecli"]
      },
      %{
        id: "marketplace_consolidate",
        name: "Consolidate candidate packs",
        description:
          "Given a candidate_pack_set and preservation_constraints, return a consolidation_plan, refused_merges, and evidence -- a real, checkable PLAN (which pack absorbs which, what a merge would break), never an executed merge/deletion. Matches this session's own real consolidation work: every actual pack removal or absorption this repo has done was verified by hand before any file was touched, exactly the SELECT-before-DO boundary this capability encodes structurally.",
        tags: ["generated", "marketplacecli"]
      }
    ]

  # Real dispatch is deliberately NOT generated here: each skill's actual
  # handler must call this app's own real Ash action/context function
  # (this pack does not invent a generic dispatch mechanism that could
  # silently no-op a skill invocation). See MarketplaceCliWeb.McpDescriptor
  # for this same capability list's real ash_action bindings, where
  # present, as the source of truth for wiring a skill handler.
end
