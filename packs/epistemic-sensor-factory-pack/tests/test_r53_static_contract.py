from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_r53_sensor_surface_is_exactly_fifty():
    sensors = sorted((ROOT / "queries" / "r53").glob("*.rq"))
    assert len(sensors) == 50
    assert sensors[0].name.startswith("551_")
    assert sensors[-1].name.startswith("600_")


def test_r53_public_semantic_and_authority_contract():
    ontology = (ROOT / "ontology.ttl").read_text()
    assert "http://www.w3.org/ns/prov#" in ontology
    assert "http://www.w3.org/ns/dqv#" in ontology
    assert "http://www.w3.org/ns/odrl/2/" in ontology
    assert "esf:CausalPropagationObservation" in ontology
    assert "esf:standingTransferred" in ontology
    assert "esf:authorityTransferred" in ontology
    assert "odrl:prohibition [ odrl:action odrl:execute ]" in ontology


def test_r53_ggen_projection_is_canonical():
    manifest = (ROOT / "ggen.toml").read_text()
    assert 'name = "causal-propagation-plan"' in manifest
    assert 'queries/610_causal_propagation_plan.rq' in manifest
    assert 'templates/causal-propagation-plan.json.tera' in manifest
    template = (ROOT / "templates" / "causal-propagation-plan.json.tera").read_text()
    assert '"consequential_do": false' in template
    assert 'standing-and-authority-do-not-propagate' in template


def main():
    test_r53_sensor_surface_is_exactly_fifty()
    test_r53_public_semantic_and_authority_contract()
    test_r53_ggen_projection_is_canonical()
    print("R53 static contract: PASS")


if __name__ == "__main__":
    main()
