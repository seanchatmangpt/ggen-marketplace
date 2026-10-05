"""Chicago-style test court for aaif-vanilla-pack and AAIF Swarm Mesh (AAIF-VANILLA-2026).

Disciplines (per ~/.claude/rules/testing-chicago-style.md):
- Real collaborators only: real rdflib RDF graph parse, real SPARQL gates, real
  filesystem I/O, real marketplace.py pack validation subprocess.
- No mocks, stubs, monkeypatches, or simulated doubles.
- Fail-witness anti-vacuity law: every gate must be subjected to an unlawful
  mutation and witnessed firing (>=1 violation row).
- Deterministic replay: rendering the pack twice produces byte-identical results.
- Syntactic compliance: all emitted AAIF manifests must parse cleanly as valid
  JSON, YAML, or Markdown conforming to the 6 AAIF projects.
- Swarm mesh validation: multi-agent swarm coordination, roles, and topology.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import rdflib
import yaml

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "aaif-vanilla-pack"
GATES_DIR = PACK / "gates"
FIXTURES_DIR = PACK / "fixtures"
TEMPLATES_DIR = PACK / "templates"
MARKETPLACE_PY = ROOT / "scripts" / "marketplace.py"
RENDER_SCRIPT = PACK / "render_aaif_pack.py"

AAIF = rdflib.Namespace("https://aaif.io/ontology#")
RDF = rdflib.RDF

GATES = sorted(GATES_DIR.glob("*.rq"))
assert len(GATES) >= 5, f"Expected at least 5 SPARQL gates in aaif-vanilla-pack, found {len(GATES)}"


def load_admitted_graph(fixture_name: str = "marketplace_agent.ttl") -> rdflib.Graph:
    g = rdflib.Graph()
    g.parse(PACK / "ontology.ttl", format="turtle")
    g.parse(FIXTURES_DIR / fixture_name, format="turtle")
    return g


def run_gate(graph: rdflib.Graph, gate_path: Path) -> list:
    query_text = gate_path.read_text(encoding="utf-8")
    return list(graph.query(query_text))


class TestChicagoRealCollaborators:
    def test_ontology_and_fixture_load_cleanly(self) -> None:
        g = load_admitted_graph("marketplace_agent.ttl")
        assert len(g) > 200, f"Expected >200 triples in admitted graph, got {len(g)}"
        agent = AAIF.MarketplaceAgent
        assert (agent, RDF.type, AAIF.Agent) in g
        names = [str(o) for o in g.objects(agent, AAIF.name)]
        assert names == ["ggen-marketplace Agent"]

    def test_swarm_fixture_loads_and_has_three_agents(self) -> None:
        g = load_admitted_graph("marketplace_swarm.ttl")
        swarm = AAIF.MarketplaceSwarm
        assert (swarm, RDF.type, AAIF.Swarm) in g
        members = list(g.objects(swarm, AAIF.hasMemberAgent))
        assert len(members) == 3
        coordinator = list(g.objects(swarm, AAIF.swarmCoordinator))
        assert len(coordinator) == 1
        assert coordinator[0] == AAIF.CoordinatorAgent


class TestAllGatesPassOnAdmittedOntology:
    @pytest.mark.parametrize("gate_path", GATES, ids=lambda p: p.stem)
    def test_gate_returns_zero_rows_on_admitted_swarm(self, gate_path: Path) -> None:
        g = load_admitted_graph("marketplace_swarm.ttl")
        rows = run_gate(g, gate_path)
        assert rows == [], f"Gate {gate_path.name} unexpectedly failed on admitted swarm: {rows}"


class TestFailWitnessAntiVacuity:
    """Anti-vacuity law: Every gate must fire on a minimal unlawful mutation."""

    def test_gate_010_trips_when_agent_name_missing(self) -> None:
        g = load_admitted_graph("marketplace_agent.ttl")
        g.remove((AAIF.MarketplaceAgent, AAIF.name, None))
        gate_path = GATES_DIR / "010_agent_required_properties.rq"
        rows = run_gate(g, gate_path)
        assert len(rows) > 0, "Gate 010 is vacuous: failed to trip when agent name was missing"

    def test_gate_020_trips_when_gateway_port_missing(self) -> None:
        g = load_admitted_graph("marketplace_agent.ttl")
        g.remove((AAIF.MarketplaceGateway, AAIF.port, None))
        gate_path = GATES_DIR / "020_gateway_binds.rq"
        rows = run_gate(g, gate_path)
        assert len(rows) > 0, "Gate 020 is vacuous: failed to trip when gateway port was missing"

    def test_gate_030_trips_when_router_primary_backend_missing(self) -> None:
        g = load_admitted_graph("marketplace_agent.ttl")
        g.remove((AAIF.MarketplaceRouter, AAIF.primaryBackend, None))
        gate_path = GATES_DIR / "030_router_backends.rq"
        rows = run_gate(g, gate_path)
        assert len(rows) > 0, "Gate 030 is vacuous: failed to trip when primaryBackend was missing"

    def test_gate_040_trips_when_swarm_lacks_coordinator(self) -> None:
        g = load_admitted_graph("marketplace_swarm.ttl")
        g.remove((AAIF.MarketplaceSwarm, AAIF.swarmCoordinator, None))
        gate_path = GATES_DIR / "040_swarm_topology.rq"
        rows = run_gate(g, gate_path)
        assert len(rows) > 0, "Gate 040 is vacuous: failed to trip when swarmCoordinator was missing"

    def test_gate_050_trips_when_swarm_member_lacks_role(self) -> None:
        g = load_admitted_graph("marketplace_swarm.ttl")
        g.remove((AAIF.CoordinatorAgent, AAIF.swarmRole, None))
        gate_path = GATES_DIR / "050_swarm_member_roles.rq"
        rows = run_gate(g, gate_path)
        assert len(rows) > 0, "Gate 050 is vacuous: failed to trip when swarmRole was missing"

    def test_gate_060_trips_when_agent_lacks_security_scheme(self) -> None:
        g = load_admitted_graph("marketplace_agent.ttl")
        g.remove((AAIF.MarketplaceAgent, AAIF.hasSecurityScheme, None))
        gate_path = GATES_DIR / "060_agent_security_schemes.rq"
        rows = run_gate(g, gate_path)
        assert len(rows) > 0, "Gate 060 is vacuous: failed to trip when security scheme was missing"

    def test_gate_070_trips_when_gateway_lacks_envelope_defense(self) -> None:
        g = load_admitted_graph("marketplace_agent.ttl")
        g.remove((AAIF.MarketplaceGateway, AAIF.hasEnvelopeDefense, None))
        gate_path = GATES_DIR / "070_envelope_defense_policy.rq"
        rows = run_gate(g, gate_path)
        assert len(rows) > 0, "Gate 070 is vacuous: failed to trip when envelope defense was missing"

    def test_gate_080_trips_when_skill_lacks_tag_contract(self) -> None:
        g = load_admitted_graph("autofde_agent.ttl")
        g.remove((AAIF.SkillFormalDecision, AAIF.skillTag, None))
        gate_path = GATES_DIR / "080_skill_attestation_contract.rq"
        rows = run_gate(g, gate_path)
        assert len(rows) > 0, "Gate 080 is vacuous: failed to trip when skillTag was missing"


class TestMarketplacePackAdmission:
    def test_marketplace_validate_admits_aaif_vanilla_pack(self) -> None:
        """Execute real marketplace.py CLI in subprocess without mocks."""
        res = subprocess.run(
            ["python3.11", str(MARKETPLACE_PY), "validate", "aaif-vanilla-pack"],
            cwd=str(ROOT),
            capture_output=True,
            text=True
        )
        assert res.returncode == 0, f"marketplace.py validate rejected pack:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
        assert "validated packs=" in res.stdout


class TestRealProjectionAndReplayLoop:
    def test_real_materialization_and_deterministic_replay(self, tmp_path: Path) -> None:
        """Run real projection twice and verify byte-identical output."""
        fixture = FIXTURES_DIR / "marketplace_swarm.ttl"
        out_dir_1 = tmp_path / "run1"
        out_dir_2 = tmp_path / "run2"

        # Run 1
        res1 = subprocess.run(
            [sys.executable, str(RENDER_SCRIPT), "--fixture", str(fixture), "--out", str(out_dir_1)],
            cwd=str(ROOT),
            capture_output=True,
            text=True
        )
        assert res1.returncode == 0, f"Render pass 1 failed: {res1.stderr}"

        # Run 2
        res2 = subprocess.run(
            [sys.executable, str(RENDER_SCRIPT), "--fixture", str(fixture), "--out", str(out_dir_2)],
            cwd=str(ROOT),
            capture_output=True,
            text=True
        )
        assert res2.returncode == 0, f"Render pass 2 failed: {res2.stderr}"

        files1 = sorted([p.relative_to(out_dir_1) for p in out_dir_1.rglob("*") if p.is_file()])
        files2 = sorted([p.relative_to(out_dir_2) for p in out_dir_2.rglob("*") if p.is_file()])
        assert files1 == files2
        assert len(files1) == 8, f"Expected 8 emitted manifests, got {len(files1)}"

        # Verify byte identity between runs
        for rel_p in files1:
            bytes1 = (out_dir_1 / rel_p).read_bytes()
            bytes2 = (out_dir_2 / rel_p).read_bytes()
            assert bytes1 == bytes2, f"Replay non-deterministic for {rel_p}"

    def test_syntax_and_specification_fidelity_of_emitted_swarm(self, tmp_path: Path) -> None:
        """Verify emitted artifacts comply with upstream AAIF project schemas."""
        fixture = FIXTURES_DIR / "marketplace_swarm.ttl"
        out_dir = tmp_path / "dist"
        subprocess.run(
            [sys.executable, str(RENDER_SCRIPT), "--fixture", str(fixture), "--out", str(out_dir)],
            cwd=str(ROOT),
            check=True
        )

        # 1. A2A Agent Card (.well-known/agent.json)
        agent_card = json.loads((out_dir / ".well-known" / "agent.json").read_text())
        assert "Coordinator" in agent_card["name"] or "Marketplace" in agent_card["name"]
        assert "capabilities" in agent_card
        assert "security_schemes" in agent_card
        assert len(agent_card["supported_interfaces"]) == 2

        # 2. MCP Servers (mcp/mcp_servers.json)
        mcp_cfg = json.loads((out_dir / "mcp" / "mcp_servers.json").read_text())
        assert "mcpServers" in mcp_cfg
        assert "filesystem" in mcp_cfg["mcpServers"]
        assert "fetch" in mcp_cfg["mcpServers"]

        # 3. Agentgateway Config (agentgateway/config.json)
        ag_cfg = json.loads((out_dir / "agentgateway" / "config.json").read_text())
        assert ag_cfg["binds"][0]["port"] == 8080

        # 4. Agent Router CRDs (k8s/agent-router.yaml)
        crds = list(yaml.safe_load_all((out_dir / "k8s" / "agent-router.yaml").read_text()))
        kinds = {c["kind"] for c in crds}
        assert "AIGatewayRoute" in kinds
        assert "AIServiceBackend" in kinds
        assert len(crds) == 7

        # 5. Goose Config & Recipe (.config/goose/*)
        goose_cfg = yaml.safe_load((out_dir / ".config" / "goose" / "config.yaml").read_text())
        assert goose_cfg["active_provider"] == "anthropic"
        assert goose_cfg["providers"]["anthropic"]["model"] == "claude-3-7-sonnet"

        recipe = yaml.safe_load((out_dir / ".config" / "goose" / "recipes" / "default.yaml").read_text())
        assert "Swarm" in recipe["title"]

        # 6. AGENTS.md
        agents_md = (out_dir / "AGENTS.md").read_text()
        assert "Open Protocol Conformances" in agents_md
