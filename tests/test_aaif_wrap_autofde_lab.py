"""Court: autofde-lab wrapped via aaif-vanilla-pack projection. No mocks."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest
import rdflib
import yaml

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "aaif-vanilla-pack"
FIXTURE = PACK / "fixtures" / "autofde_agent.ttl"
TARGET = Path.home() / "autofde-lab"
GOOSE = ROOT / "bin" / "goose"

pytestmark = pytest.mark.skipif(not TARGET.exists(), reason="autofde-lab checkout absent")


def test_projection_is_ggen_cli_output_byte_identical(tmp_path: Path) -> None:
    """The files in autofde-lab are exactly what `ggen sync run` generates."""
    import shutil

    proj = ROOT / "projections" / "autofde-lab"
    # ggen forbids '..' paths, so run in a copy of the project with real copies of its inputs.
    work = tmp_path / "proj"
    work.mkdir()
    shutil.copy(proj / "ggen.toml", work / "ggen.toml")
    shutil.copy(FIXTURE, work / "autofde_agent.ttl")
    shutil.copytree(PACK / "templates", work / "templates")
    res = subprocess.run(["ggen", "sync", "run", "--format", "json"],
                         cwd=work, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    out = json.loads(res.stdout[res.stdout.index("{"):])
    assert ".well-known/agent.json" in out["written"]
    for rel in (".well-known/agent.json", "agentgateway/config.json",
                "k8s/agent-router.yaml", ".config/goose/recipes/default.yaml",
                "mcp/mcp_servers.json", ".goosehints"):
        assert (TARGET / rel).read_text() == (work / rel).read_text(), f"drift: {rel}"
    assert (TARGET / "docs/aaif/AGENTS.generated.md").read_text() == (work / "AGENTS.md").read_text()


def test_a2a_sdk_parses_rendered_agent_card() -> None:
    from a2a.types import AgentCard
    from google.protobuf.json_format import ParseDict

    data = json.loads((TARGET / ".well-known/agent.json").read_text())
    assert data["name"] == "autofde-lab Decision Agent"
    assert len(data.get("skills", [])) >= 1
    assert data["skills"][0]["id"] == "formal_decision"
    assert data["skills"][0]["name"] == "Formal Decision Planning"

    card = ParseDict(data, AgentCard(), ignore_unknown_fields=True)
    assert card.name == "autofde-lab Decision Agent"
    assert len(card.supported_interfaces) >= 1

    # Verify MCP server contains autofde decision fabric
    mcp_data = json.loads((TARGET / "mcp/mcp_servers.json").read_text())
    assert "autofde_decision_fabric" in mcp_data.get("mcpServers", {})
    autofde_mcp = mcp_data["mcpServers"]["autofde_decision_fabric"]
    assert autofde_mcp["command"] == "python"
    assert "-m" in autofde_mcp["args"] and "autofde_lab.aaif" in autofde_mcp["args"]



def test_goose_binary_validates_rendered_recipe() -> None:
    res = subprocess.run(
        [str(GOOSE), "recipe", "validate", str(TARGET / ".config/goose/recipes/default.yaml")],
        capture_output=True, text=True,
    )
    assert res.returncode == 0, res.stderr + res.stdout
    assert "recipe file is valid" in res.stdout


def test_agent_router_crds_are_envoy_ai_gateway_kinds() -> None:
    docs = list(yaml.safe_load_all((TARGET / "k8s/agent-router.yaml").read_text()))
    assert docs and all(d["apiVersion"].startswith("aigateway.envoyproxy.io/") for d in docs)
    assert {"GatewayConfig", "BackendSecurityPolicy", "AIServiceBackend"} <= {d["kind"] for d in docs}


def test_pack_gates_admit_fixture_and_refuse_mutation() -> None:
    def violations(graph: rdflib.Graph) -> int:
        n = 0
        for gate in sorted((PACK / "gates").glob("0[1-5]0_*.rq")):
            n += len(list(graph.query(gate.read_text())))
        return n

    g = rdflib.Graph()
    g.parse(str(FIXTURE), format="turtle")
    base = violations(g)
    assert base == 0, "gates reject the valid autofde fixture"

    # Test gate 020/030 tripwire
    mutated = FIXTURE.read_text()
    mutated = re.sub(r'aaif:primaryBackend "[^"]+" ;\s*', "", mutated)
    mutated = re.sub(r'aaif:port \d+ ;\s*', "", mutated)
    m = rdflib.Graph()
    m.parse(data=mutated, format="turtle")
    assert violations(m) > base, "gates did not refuse mutated gateway/router fixture"

    # Test swarm gate 040/050 tripwire
    mutated_swarm = FIXTURE.read_text()
    mutated_swarm = re.sub(r'aaif:swarmRole "[^"]+" ;\s*', "", mutated_swarm)
    m_swarm = rdflib.Graph()
    m_swarm.parse(data=mutated_swarm, format="turtle")
    assert violations(m_swarm) > base, "gates did not refuse unassigned swarmRole"

