from pathlib import Path

def test_contract_surface_exists():
    root=Path(__file__).parents[1]
    required=['pack.toml','ontology.ttl','ggen.toml','queries/10-qualified-source.rq','queries/20-lineage-frontier.rq','queries/30-clean-plan.rq','gates/01-qualified-source.rq','gates/02-no-force-no-do.rq']
    for rel in required:
        assert (root/rel).exists(), rel

def test_no_force_or_actuation():
    text=(Path(__file__).parents[1]/'ontology.ttl').read_text()
    assert 'forcePushAllowed false' in text
    assert 'actuationPerformed false' in text
    assert 'semanticDelta 0' in text
