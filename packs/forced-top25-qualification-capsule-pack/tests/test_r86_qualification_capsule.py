import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_public_semantics_and_authority_fence():
    ontology = (ROOT / "ontology.ttl").read_text()
    assert "http://www.w3.org/ns/prov#" in ontology
    assert 'r86:authority "VERIFY|CONSTRUCT"' in ontology
    assert "r86:consequentialDo false" in ontology

def test_ready_set_is_lawful_and_ordered():
    query = (ROOT / "queries/10-capsule-ready-set.rq").read_text()
    assert 'fta:compatibilityState "COMPATIBLE_READY"' in query
    assert "FILTER NOT EXISTS" in query
    assert "ORDER BY ?rank ?repo" in query

def test_template_is_deterministic_and_zero_do():
    template = (ROOT / "templates/qualification-capsule.json.tmpl").read_text()
    assert "for_each: capsule_ready_set" in template
    assert "determinism: true" in template
    assert '"authority":"VERIFY|CONSTRUCT"' in template
    assert '"consequential_do":false' in template
    assert '"hosted_wrapper_required_for_semantic_standing":false' in template

def test_hosted_preexec_remains_observation_not_consumer_refusal():
    observations = json.loads((ROOT / "fixtures/hosted-preexec-observations.json").read_text())
    assert len(observations) >= 2
    assert all(x["standing"] == "BUILD_BROKEN[HOSTED_WORKFLOW_PREEXEC]" for x in observations)
