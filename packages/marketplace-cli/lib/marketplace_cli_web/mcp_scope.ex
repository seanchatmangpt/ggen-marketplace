defmodule MarketplaceCliWeb.McpScope do
  @moduledoc """
  Generated MCP router scope for `MarketplaceCli`, from one admitted
  ema:CapabilitySurface. Mount in your router:

      import MarketplaceCliWeb.McpScope

      scope "/mcp" do
        pipe_through([:api])
        MarketplaceCliWeb.McpScope.mount(__MODULE__)
      end

  Real tools exposed: `:marketplace_search`, `:marketplace_qualify_pack`, `:marketplace_consolidate`.

  NO AUDIT PLUG configured on this surface (ema:mcpAuditPlugModule was
  absent from the spec) -- every MCP call through this scope is
  unaudited. This is a disclosed gap, not a silent default: add an
  ema:mcpAuditPlugModule row to the spec (mirroring
  XaasWeb.Plugs.AuditMcpToolCall's real convention) before treating this
  surface as production-ready.

  """

  defmacro mount(_router_module) do
    quote do
      forward("/", AshAi.Mcp.Router,
        tools: [:marketplace_search, :marketplace_qualify_pack, :marketplace_consolidate],
        protocol_version_statement: "2024-11-05",
        otp_app: :marketplace_cli
      )
    end
  end
end
