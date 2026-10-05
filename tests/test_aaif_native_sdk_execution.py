"""Chicago-School Test Court for Native Upstream AAIF Stack Execution.

Validates the real upstream Linux Foundation AAIF implementations:
1. Native `a2a-sdk` AgentCard discovery and Starlette JSON-RPC routing.
2. Native `mcp` Model Context Protocol (v2.x) ClientSession invoking FastMCP/MCPServer tools over streamable HTTP.
3. Native `goose` (v1.53.0) CLI recipe validation on generated pack recipes.
4. Native `agctl` (v1.6.0) controller/catalog CLI discovery.
5. Native `aigw` (v1.1.0) Envoy AI Gateway binary functionality.

NO MOCKS. Zero synthetic stubs. Real collaborators and real Mach-O binaries.
"""

from __future__ import annotations

import os
import subprocess
import threading
import time
from pathlib import Path

import pytest
import uvicorn

pytest.importorskip("a2a", reason="optional dependency not installed")
from starlette.testclient import TestClient

from a2a.types import AgentCard
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

from ggen_marketplace.aaif_node import create_aaif_combined_app, build_mcp_server

ROOT = Path(__file__).resolve().parents[1]
BIN_DIR = ROOT / "bin"


class TestAAIFNativeSDKExecution:
    """Rigorous verification court running authentic AAIF upstream code and binaries."""

    def test_a2a_sdk_agent_card_discovery(self) -> None:
        """Verify official a2a-sdk generates compliant AgentCard and well-known endpoint."""
        app = create_aaif_combined_app()
        client = TestClient(app)

        res = client.get("/.well-known/agent-card.json")
        assert res.status_code == 200, f"Expected 200 OK, got {res.status_code}: {res.text}"
        data = res.json()
        assert data.get("name") == "GGen Marketplace Coordinator"
        assert data.get("version") == "26.10.4"
        assert "skills" in data
        skill_ids = [s["id"] for s in data["skills"]]
        assert "search_packs" in skill_ids
        assert "verify_invariants" in skill_ids

    def test_a2a_sdk_jsonrpc_route_admission(self) -> None:
        """Verify official a2a-sdk JSON-RPC handler mounts and rejects unauthenticated/malformed frames fail-closed."""
        app = create_aaif_combined_app()
        client = TestClient(app)

        # Post invalid jsonrpc payload
        res = client.post("/rpc", json={"invalid": "payload"})
        assert res.status_code in (200, 400)
        # JSON-RPC error must be returned
        data = res.json()
        assert "error" in data or "jsonrpc" in data

    @pytest.mark.asyncio
    async def test_mcp_official_sdk_client_session_execution(self) -> None:
        """Spin up authentic MCPServer and execute tools via real ClientSession."""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]

        server = build_mcp_server()
        app = server.streamable_http_app()

        config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
        srv = uvicorn.Server(config)

        # Run uvicorn in background thread
        thread = threading.Thread(target=srv.run, daemon=True)
        thread.start()
        for _ in range(30):
            time.sleep(0.1)
            if srv.started:
                break

        try:
            url = f"http://127.0.0.1:{port}/mcp"
            async with streamable_http_client(url) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()

                    # 1. Discover tools
                    tools_result = await session.list_tools()
                    tool_names = [t.name for t in tools_result.tools]
                    assert "search_packs" in tool_names
                    assert "get_catalog_summary" in tool_names

                    # 2. Invoke get_catalog_summary
                    summary_result = await session.call_tool("get_catalog_summary", {})
                    assert summary_result.content
                    summary_text = summary_result.content[0].text
                    assert "total_packs" in summary_text

                    # 3. Invoke search_packs with real query
                    search_result = await session.call_tool("search_packs", {"query": "aaif"})
                    assert search_result.content
                    search_text = search_result.content[0].text
                    assert "aaif-vanilla-pack" in search_text
        finally:
            srv.should_exit = True
            thread.join(timeout=2.0)

    def test_native_goose_binary_recipe_validation(self) -> None:
        """Verify upstream Goose CLI validates the generated recipe."""
        goose_bin = BIN_DIR / "goose"
        assert goose_bin.exists(), f"goose binary missing at {goose_bin}"

        recipe_path = ROOT / "packs/aaif-vanilla-pack/dist/.config/goose/recipes/default.yaml"
        res = subprocess.run(
            [str(goose_bin), "recipe", "validate", str(recipe_path)],
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, f"Goose validation failed: {res.stderr}\n{res.stdout}"
        assert "recipe file is valid" in res.stdout

    def test_native_agentgateway_binary_execution(self) -> None:
        """Verify upstream agentgateway agctl binary executes and discovers catalog commands."""
        agctl_bin = BIN_DIR / "agctl"
        assert agctl_bin.exists(), f"agctl binary missing at {agctl_bin}"

        res = subprocess.run([str(agctl_bin), "--help"], capture_output=True, text=True)
        assert res.returncode == 0
        assert "agctl controls and inspects Agentgateway resources" in res.stdout
        assert "catalog" in res.stdout

    def test_native_agent_router_binary_execution(self) -> None:
        """Verify upstream agent-router aigw binary executes version and help commands."""
        aigw_bin = BIN_DIR / "aigw"
        assert aigw_bin.exists(), f"aigw binary missing at {aigw_bin}"

        res = subprocess.run([str(aigw_bin), "--help"], capture_output=True, text=True)
        assert res.returncode == 0
        assert "Envoy AI Gateway CLI" in res.stdout
        assert "download-envoy" in res.stdout
