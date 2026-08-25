from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]

def test_pack_identity_matches_directory():
    data = tomllib.loads((ROOT / "pack.toml").read_text())
    assert data["pack"]["name"] == ROOT.name


def test_factory_is_ggen_owned():
    cfg = tomllib.loads((ROOT / "ggen.toml").read_text())
    assert cfg["ontology"]["source"] == "ontology.ttl"
    rules = cfg["generation"]["rules"]
    assert any(r["name"] == "sensor-family-plan" for r in rules)


def test_public_ontology_and_authority_bounds():
    ttl = (ROOT / "ontology.ttl").read_text()
    for iri in ("http://www.w3.org/ns/prov#", "http://www.w3.org/ns/dqv#", "http://www.w3.org/ns/odrl/2/"):
        assert iri in ttl
    assert "odrl:prohibition [ odrl:action odrl:execute ]" in ttl


def test_generated_plan_is_consequence_not_source():
    template = (ROOT / "templates/sensor-family-plan.json.tera").read_text()
    assert '"actuation_performed":false' in template
    assert '"sensors":[' in template
