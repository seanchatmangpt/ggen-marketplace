"""Chicago tests for the AuthZEN/SPIFFE absorption pack.

These tests read the real marketplace pack and its canonical qualification
fixtures. They intentionally do not mock the filesystem or synthesize a
second policy/identity implementation.
"""
from __future__ import annotations

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "authzen-spiffe-absorption-pack"
QUALIFICATION = PACK / "qualification"


def load_json(name: str) -> dict:
    return json.loads((QUALIFICATION / name).read_text(encoding="utf-8"))


def test_authzen_figure_14_wire_shape_is_preserved_exactly() -> None:
    fixture = load_json("canonical_authzen_figure_14.json")

    assert fixture["request"] == {
        "subject": {"type": "user", "id": "alice@example.com"},
        "resource": {"type": "account", "id": "123"},
        "action": {
            "name": "can_read",
            "properties": {"method": "GET"},
        },
        "context": {"time": "1985-10-26T01:22-07:00"},
    }
    assert "type" not in fixture["request"]["action"]
    assert "id" not in fixture["request"]["action"]
    assert fixture["authority"] == "NONE"
    assert fixture["consequence"] == "EVIDENCE_ONLY"


def test_spiffe_published_identity_example_preserves_exact_identity_components() -> None:
    fixture = load_json("canonical_spiffe_workload_identity.json")

    assert fixture["spiffe_id"] == "spiffe://prod.acme.com/billing/api"
    assert fixture["trust_domain"] == "prod.acme.com"
    assert fixture["path"] == "/billing/api"
    assert fixture["svid_profile"] == "X.509-SVID"
    assert fixture["authority"] == "NONE"
    assert fixture["consequence"] == "EVIDENCE_ONLY"


def test_canonical_examples_are_bound_to_final_authzen_and_immutable_spiffe_sources() -> None:
    lock = tomllib.loads((PACK / "source-lock.toml").read_text(encoding="utf-8"))

    assert lock["authzen"]["version"] == "1.0 Final"
    assert lock["authzen"]["stable_uri"] == "https://openid.net/specs/authorization-api-1_0.html"
    assert lock["authzen"]["identity_class"] == "standards_artifact"

    assert lock["spiffe"]["repository"] == "spiffe/spiffe"
    assert len(lock["spiffe"]["commit_sha"]) == 40
    assert lock["spiffe"]["identity_class"] == "git_commit"


def test_external_allow_plus_allocation_still_cannot_construct_do_authority() -> None:
    fixture = load_json("allocation_plus_allow.json")

    assert fixture["allocation_evidence"] is True
    assert fixture["authzen_decision"] is True
    assert fixture["local_certificate"] is None
    assert fixture["expected"] == "REFUSE"
    assert fixture["reason"] == "allocation_plus_policy_evidence_is_not_do_authority"
