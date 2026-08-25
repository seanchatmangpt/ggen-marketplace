from pathlib import Path

def test_contract_surface_exists():
    root=Path(__file__).parents[1]
    required=['pack.toml','ontology.ttl','ggen.toml','queries/10-admitted-cells.rq','queries/20-compatible-frontier.rq','queries/30-clean-frontier.rq','gates/01-exact-subject.rq','gates/02-no-ambient-do.rq']
    for rel in required:
        assert (root/rel).exists(), rel

def test_authority_is_non_actuating():
    text=(Path(__file__).parents[1]/'ontology.ttl').read_text()
    assert 'actuationPerformed false' in text
    assert 'authority "SELECT|CONSTRUCT|VERIFY"' in text
