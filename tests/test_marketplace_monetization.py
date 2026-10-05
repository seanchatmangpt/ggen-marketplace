"""Real-file tests for the monetization registry loader (no mocks, tmp_path fixtures)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import marketplace_monetization as mm

VALID = """\
schema_version = "1.0.0"

[monetization]
backend = "sim"
billing_authorities = ["GOOGLE_CLOUD_MARKETPLACE"]
provider_id = "demo-provider"
unit_price_usd = 0.05

[solutions.gcp-marketplace-saas]
backend = "real"
billing_authorities = ["AWS_MARKETPLACE"]
provider_id = "acme-corp"
unit_price_usd = 1.25
plan = "enterprise"
"""


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / mm.REGISTRY_RELATIVE
    path.write_text(text, encoding="utf-8")
    return path


def test_valid_registry_parses(tmp_path: Path) -> None:
    write(tmp_path, VALID)
    config, problems = mm.load(tmp_path)
    assert problems == []
    effective = mm.effective_for(config, "gcp-marketplace-saas")
    assert effective["backend"] == "real"
    assert effective["billing_authorities"] == ["AWS_MARKETPLACE"]
    assert effective["unit_price_usd"] == 1.25
    assert effective["plan"] == "enterprise"
    assert mm.entry_issues(config) == []


def test_dual_authority_refused(tmp_path: Path) -> None:
    write(
        tmp_path,
        VALID.replace('billing_authorities = ["AWS_MARKETPLACE"]', 'billing_authorities = ["AWS_MARKETPLACE", "IBM_MARKETPLACE"]'),
    )
    config, problems = mm.load(tmp_path)
    assert problems == []
    codes = [i.split(":")[1] for i in mm.entry_issues(config)]
    assert "REFUSED_MONETIZATION_AUTHORITY_CARDINALITY" in codes


def test_unknown_authority_refused(tmp_path: Path) -> None:
    write(tmp_path, VALID.replace("AWS_MARKETPLACE", "ACME_BILLING"))
    config, _ = mm.load(tmp_path)
    issues = mm.entry_issues(config)
    assert any("REFUSED_MONETIZATION_AUTHORITY_UNKNOWN" in i and i.endswith(":ACME_BILLING") for i in issues)


def test_unknown_backend_refused(tmp_path: Path) -> None:
    write(tmp_path, VALID.replace('backend = "real"', 'backend = "hybrid"'))
    config, _ = mm.load(tmp_path)
    assert any("REFUSED_MONETIZATION_BACKEND_UNKNOWN" in i and "'hybrid'" in i for i in mm.entry_issues(config))


def test_missing_file_empty_defaults(tmp_path: Path) -> None:
    config, problems = mm.load(tmp_path)
    assert config == {}
    assert problems == []
    assert mm.entry_issues(config) == []
    effective = mm.effective_for(config, "anything")
    assert effective == dict(mm.DEFAULTS)
    assert effective["backend"] == "sim"
    assert effective["unit_price_usd"] == 0.05


@pytest.mark.parametrize("bad_price", ["0.0", "-0.05"])
def test_nonpositive_price_refused(tmp_path: Path, bad_price: str) -> None:
    write(tmp_path, VALID.replace("unit_price_usd = 1.25", f"unit_price_usd = {bad_price}"))
    config, _ = mm.load(tmp_path)
    codes = [i.split(":")[1] for i in mm.entry_issues(config)]
    assert "REFUSED_MONETIZATION_PRICE_INVALID" in codes


def test_unknown_key_refused(tmp_path: Path) -> None:
    write(tmp_path, VALID.replace('plan = "enterprise"', 'plan = "enterprise"\nsecret_sauce = true'))
    config, _ = mm.load(tmp_path)
    assert any("REFUSED_MONETIZATION_UNKNOWN_KEY:gcp-marketplace-saas:secret_sauce" in i for i in mm.entry_issues(config))
