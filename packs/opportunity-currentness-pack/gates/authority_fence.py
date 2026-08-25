from pathlib import Path
text=Path(__file__).parents[1].joinpath('ontology.ttl').read_text()
assert 'ocp:actuationPerformed false' in text,'REFUSED[DO_LEAK]'
assert 'ocp:networkAllowed false' in text,'REFUSED[NETWORK_LEAK]'
assert 'ocp:authority "OBSERVE|VERIFY|CONSTRUCT"' in text,'REFUSED[AUTHORITY_DRIFT]'
