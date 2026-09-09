#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
queries = sorted((ROOT / "queries" / "r51").glob("*.rq"))
assert len(queries) == 50
for q in queries:
    text = q.read_text()
    assert "SELECT" in text.upper(), q
    assert "PREFIX esf:" in text, q
    if "xsd:" in text:
        assert "PREFIX xsd:" in text, q

ontology = (ROOT / "ontology.ttl").read_text()
assert "esf:transitivePropagationFamily" in ontology
assert "odrl:prohibition [ odrl:action odrl:execute ]" in ontology
manifest = (ROOT / "ggen.toml").read_text()
assert 'name = "transitive-propagation-plan"' in manifest
print("R51_STATIC_ALIVE sensors=50")
