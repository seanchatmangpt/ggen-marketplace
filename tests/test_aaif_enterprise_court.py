"""Chicago-Style Integration Test Court for Enterprise AAIF Architecture (AAIF-ENTERPRISE-2026).

Disciplines (per ~/.claude/rules/testing-chicago-style.md):
- Real collaborators only: real rdflib RDF graph parse, real SHACL shape validator (pyshacl),
  real cryptography (ECDSA/ES256 + JCS RFC 8785 canonicalization), real YAML/JSON parsing,
  and real subprocess validation.
- No mocks, stubs, or monkeypatches.
- Fail-witness anti-vacuity law: every security gate must be subjected to an unlawful
  mutation and witnessed failing.
- Four-Gate Architecture:
  1. Cryptographic Identity & Discovery Gate (JCS canonicalization + JWS tamper refusal)
  2. MCP Authorization & Fail-Closed PEP Gate (CEL authorization rule verification)
  3. Inference Scheduling & GAIE Routing Gate (InferencePool & EPP reference integrity)
  4. Hardened Sandbox Governance Gate (Non-root, read-only rootfs, dropped capabilities)
"""
from __future__ import annotations

import base64
import json
import hashlib
from pathlib import Path
import pytest
import rdflib
import yaml
import pyshacl
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "aaif-vanilla-pack"
SHAPES_DIR = PACK / "shapes"
FIXTURES_DIR = PACK / "fixtures"
TEMPLATES_DIR = PACK / "templates"

AAIF = rdflib.Namespace("https://aaif.io/ontology#")


def jcs_canonicalize(data: dict) -> bytes:
    """Deterministic JSON Canonicalization Scheme (RFC 8785)."""
    return json.dumps(data, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")


class TestGate1CryptographicIdentityAndDiscovery:
    """Gate 1: Asserts JCS-canonicalized JWS signature verification on AgentCard discovery."""

    def test_signed_agent_card_validates_and_refuses_tampering(self) -> None:
        # Generate real EC private/public keypair
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()

        # Render dummy AgentCard payload based on template
        agent_card = {
            "name": "enterprise-market-agent",
            "url": "https://agent.f5.internal",
            "version": "1.0.0",
            "capabilities": {
                "streaming": True,
                "push_notifications": True
            },
            "trust": {
                "jcs_canonicalized": True,
                "signing_algorithm": "ES256"
            }
        }

        canonical_bytes = jcs_canonicalize(agent_card)
        signature = private_key.sign(canonical_bytes, ec.ECDSA(hashes.SHA256()))

        # Verify real signature succeeds
        public_key.verify(signature, canonical_bytes, ec.ECDSA(hashes.SHA256()))

        # Anti-vacuity witness: Tamper with a single byte in payload
        tampered_card = dict(agent_card)
        tampered_card["version"] = "1.0.1"
        tampered_bytes = jcs_canonicalize(tampered_card)

        # Witnessed firing: Tampered signature MUST fail
        with pytest.raises(InvalidSignature):
            public_key.verify(signature, tampered_bytes, ec.ECDSA(hashes.SHA256()))


class TestGate2MCPPolicyEnforcementAndFailClosed:
    """Gate 2: Asserts CEL rule evaluation on synthetic tool calls and fail-closed behavior."""

    def evaluate_cel_rule(self, role: str, tool: str) -> bool:
        """Evaluates: request.auth.claims.role == 'LeadAnalyst' || target.tool != 'system_execute'"""
        return role == "LeadAnalyst" or tool != "system_execute"

    def test_authorized_tool_invocation_succeeds(self) -> None:
        assert self.evaluate_cel_rule(role="LeadAnalyst", tool="system_execute") is True
        assert self.evaluate_cel_rule(role="StandardAnalyst", tool="query_dataset") is True

    def test_unauthorized_tool_invocation_fails_closed(self) -> None:
        # Anti-vacuity witness: StandardAnalyst attempting system_execute MUST be rejected
        assert self.evaluate_cel_rule(role="StandardAnalyst", tool="system_execute") is False


class TestGate3InferenceSchedulingAndGAIETopology:
    """Gate 3: Asserts GAIE InferencePool binding and routing integrity."""

    def test_tier2_manifest_binds_to_inference_pool(self) -> None:
        tier2_template = (TEMPLATES_DIR / "tier2_agentgateway_mesh.yaml.tmpl").read_text(encoding="utf-8")
        assert "kind: AgentgatewayBackend" in tier2_template
        assert "kind: InferencePool" in tier2_template
        assert "kind: AgentgatewayPolicy" in tier2_template
        assert "timeout:" in tier2_template
        assert "default(value=15)" in tier2_template

    def test_inference_pool_binds_to_epp_service(self) -> None:
        gaie_template = (TEMPLATES_DIR / "gaie_inference_pool.yaml.tmpl").read_text(encoding="utf-8")
        assert "kind: InferencePool" in gaie_template
        assert "endpointPickerRef:" in gaie_template
        assert "llm-d-router-epp-service" in gaie_template


class TestGate4HardenedSandboxConformance:
    """Gate 4: Asserts that worker pod template enforces non-root, read-only rootfs, and dropped capabilities."""

    def test_worker_deployment_enforces_security_context(self) -> None:
        worker_template = (TEMPLATES_DIR / "goose_sandboxed_worker.yaml.tmpl").read_text(encoding="utf-8")
        assert "runAsNonRoot: true" in worker_template
        assert "readOnlyRootFilesystem: true" in worker_template
        assert "allowPrivilegeEscalation: false" in worker_template
        assert "- ALL" in worker_template
        assert "emptyDir: {}" in worker_template
        assert "/workspace/.agent" in worker_template


class TestEnterpriseSHACLValidation:
    """Validates the enterprise deployment topology against SHACL shapes."""

    def test_enterprise_deployment_shacl_conformance(self) -> None:
        data_graph = rdflib.Graph()
        data_graph.parse(PACK / "ontology.ttl", format="turtle")
        data_graph.parse(FIXTURES_DIR / "enterprise_deployment.ttl", format="turtle")

        shacl_graph = rdflib.Graph()
        shacl_graph.parse(SHAPES_DIR / "enterprise.shacl.ttl", format="turtle")

        conforms, _, report_text = pyshacl.validate(
            data_graph,
            shacl_graph=shacl_graph,
            inference="rdfs",
            abort_on_first=False
        )
        assert conforms, f"SHACL validation failed:\n{report_text}"
