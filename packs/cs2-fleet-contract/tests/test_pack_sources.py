from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_pack_keeps_exact_subject():
    text = (ROOT / "ontology.ttl").read_text()
    assert "cs2:RFC-CS2-001" in text

def test_three_distribution_targets_are_declared():
    text = (ROOT / "ontology.ttl").read_text()
    for repo in ("seanchatmangpt/ggen-marketplace", "seanchatmangpt/ash_a2a", "seanchatmangpt/xaas"):
        assert repo in text

def test_elixir_adapter_rejects_divergent_identity():
    text = (ROOT / "adapters/elixir/lib/cs2_fleet_contract.ex").read_text()
    assert 'authority_ceiling" => "CONSTRUCT"' in text
    assert "divergent CS2 fleet contract" in text
