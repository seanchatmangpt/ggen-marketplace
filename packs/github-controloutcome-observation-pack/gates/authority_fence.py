from pathlib import Path
text = Path(__file__).parents[1].joinpath('ontology.ttl').read_text()
assert 'gco:actuationPerformed true' not in text, 'REFUSED[DO_AUTHORITY_LEAK]'
assert 'gco:authority "OBSERVE|VERIFY"' in text, 'REFUSED[MISSING_OBSERVATION_AUTHORITY]'
