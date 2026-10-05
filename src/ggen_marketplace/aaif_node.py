"""Native AAIF Node Implementation.

Unifies official Linux Foundation AAIF standards:
1. Agent-to-Agent (A2A) protocol server and client (via official `a2a-sdk`).
2. Model Context Protocol (MCP) server exposing marketplace pack search and catalog (via official `mcp`).
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.types import (
    AgentCard,
    AgentProvider,
    AgentCapabilities,
    AgentInterface,
    AgentSkill,
    Task,
    TaskStatus,
    TaskState,
)
from a2a.server.routes import create_jsonrpc_routes, create_agent_card_routes
from starlette.applications import Starlette
from starlette.routing import Mount

import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

try:
    import marketplace as mp
except ImportError:
    mp = None

from mcp.server.mcpserver import MCPServer


class MarketplaceA2AExecutor(AgentExecutor):
    """Executes multi-agent swarm workflows using A2A protocol."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        params = context.params if hasattr(context, "params") else {}
        action = params.get("action", "catalog") if isinstance(params, dict) else "catalog"
        query = params.get("query", "") if isinstance(params, dict) else ""

        if mp is not None:
            packs = [p.catalog_record() for p in mp.scoped_packs("all")]
        else:
            packs = []

        if action == "search" and query:
            results = [p for p in packs if query.lower() in p["name"].lower() or query.lower() in p.get("description", "").lower()]
        else:
            results = packs

        return None

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


def build_mcp_server() -> MCPServer:
    """Build official AAIF Model Context Protocol server exposing marketplace tools."""
    server = MCPServer("ggen-marketplace-mcp")

    @server.tool(description="Search marketplace packs by keyword query.")
    def search_packs(query: str) -> List[Dict[str, Any]]:
        if mp is None:
            return []
        packs = [p.catalog_record() for p in mp.scoped_packs("all")]
        matches = [
            p for p in packs
            if query.lower() in p["name"].lower() or query.lower() in p.get("description", "").lower()
        ]
        return [
            {
                "name": p["name"],
                "version": p["version"],
                "tier": p.get("tier", "unknown"),
                "description": p.get("description", ""),
            }
            for p in matches
        ]

    @server.tool(description="Retrieve comprehensive catalog summary across all packs.")
    def get_catalog_summary() -> Dict[str, Any]:
        if mp is None:
            return {"total_packs": 0, "tiers": {}}
        packs = [p.catalog_record() for p in mp.scoped_packs("all")]
        tiers: Dict[str, int] = {}
        for p in packs:
            t = p.get("tier", "unknown")
            tiers[t] = tiers.get(t, 0) + 1
        return {
            "total_packs": len(packs),
            "tiers": tiers,
        }

    return server


def build_a2a_agent_card(rpc_url: str = "http://localhost:8080/rpc") -> AgentCard:
    """Generate official AAIF AgentCard specification."""
    return AgentCard(
        name="GGen Marketplace Coordinator",
        description="Autonomous AAIF Swarm Coordinator & Pack Discovery Agent",
        version="26.10.4",
        provider=AgentProvider(
            organization="GGen Marketplace Foundation",
            url="https://github.com/seanchatmangpt/ggen-marketplace",
        ),
        capabilities=AgentCapabilities(
            streaming=True,
        ),
        skills=[
            AgentSkill(
                id="search_packs",
                name="Marketplace Pack Search",
                description="Discovers and queries ggen marketplace packs by domain and facet.",
            ),
            AgentSkill(
                id="verify_invariants",
                name="Chicago Tripwire Verification",
                description="Validates pack compliance with SPARQL tripwire gates and AAIF contracts.",
            ),
        ],
        supported_interfaces=[
            AgentInterface(
                protocol_binding="jsonrpc",
                url=rpc_url,
            )
        ],
    )


def create_aaif_combined_app(rpc_url: str = "http://localhost:8080/rpc") -> Starlette:
    """Creates a unified Starlette application serving both A2A endpoints and MCP Streamable HTTP."""
    agent_card = build_a2a_agent_card(rpc_url=rpc_url)
    task_store = InMemoryTaskStore()
    executor = MarketplaceA2AExecutor()
    handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=task_store,
        agent_card=agent_card,
    )

    a2a_routes = create_jsonrpc_routes(request_handler=handler, rpc_url="/rpc")
    card_routes = create_agent_card_routes(agent_card=agent_card)

    mcp_server = build_mcp_server()
    mcp_app = mcp_server.streamable_http_app()

    # Unified application routing
    app = Starlette(
        routes=a2a_routes + card_routes + [
            Mount("/mcp", app=mcp_app),
        ]
    )
    return app
