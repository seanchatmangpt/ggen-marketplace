from __future__ import annotations

import copy
import importlib.util
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_source_authority.py"

spec = importlib.util.spec_from_file_location("verify_source_authority", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def admitted_payload() -> dict[str, object]:
    config = tomllib.loads((ROOT / "marketplace.toml").read_text(encoding="utf-8"))
    return {"q_config": 1, "standing": "ADMITTED", "config": config}


def refusal(payload: dict[str, object]) -> str:
    with pytest.raises(SystemExit) as exc:
        module.verify(payload)
    return str(exc.value)


def test_current_marketplace_has_one_canonical_pack_authority() -> None:
    receipt = module.verify(admitted_payload())
    assert receipt["standing"] == "ADMITTED"
    assert receipt["canonical_repository"] == "seanchatmangpt/ggen-marketplace"
    assert receipt["canonical_branch"] == "main"
    assert receipt["mirrors_are_provenance_only"] is True
    assert receipt["ggen_repository"] == "seanchatmangpt/ggen"
    assert receipt["ggen_version"] == "v26.8.11"
    assert receipt["ggen_release_commit"] == "402cecdff8784767eb9f26e235d87c759610c066"
    assert receipt["do_authority"] is False
    assert receipt["pack_count"] > 0
    assert receipt["pack_file_count"] >= receipt["pack_count"]
    assert len(receipt["pack_corpus_sha256"]) == 64


def test_mirror_cannot_be_promoted_to_authority() -> None:
    payload = copy.deepcopy(admitted_payload())
    payload["config"]["source_authority"]["mirrors_are_provenance_only"] = False
    assert "REFUSED:MIRROR_AUTHORITY_ESCALATION" in refusal(payload)


def test_ggen_release_requires_exact_commit_identity() -> None:
    payload = copy.deepcopy(admitted_payload())
    payload["config"]["ggen"]["release_commit"] = "v26.8.11"
    assert "REFUSED:GGEN_RELEASE_COMMIT_IDENTITY" in refusal(payload)


def test_pack_authority_cannot_move_back_to_ggen() -> None:
    payload = copy.deepcopy(admitted_payload())
    payload["config"]["source_authority"]["repository"] = "seanchatmangpt/ggen"
    assert "REFUSED:SOURCE_AUTHORITY_REPOSITORY" in refusal(payload)
