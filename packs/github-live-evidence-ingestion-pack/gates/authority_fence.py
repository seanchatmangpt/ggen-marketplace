from pathlib import Path
text=Path(__file__).parents[1].joinpath('ontology.ttl').read_text()
assert 'gli:actuationPerformed false' in text,'REFUSED[MISSING_NO_ACTUATION_ASSERTION]'
assert 'gli:networkAllowed false' in text,'REFUSED[MISSING_NETWORK_FENCE]'
assert 'gli:authority "OBSERVE|VERIFY|CONSTRUCT"' in text,'REFUSED[AUTHORITY_DRIFT]'
