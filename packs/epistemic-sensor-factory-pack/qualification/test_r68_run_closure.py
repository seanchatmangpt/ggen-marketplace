from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "ontology.r68-run-closure-observability.ttl"
FIXTURE = ROOT / "fixtures" / "r68-run-closure.ttl"
QUERIES = sorted((ROOT / "queries").glob("20[0-4][0-9]_r68_*.rq")) + sorted((ROOT / "queries").glob("2050_r68_*.rq"))

assert ONTOLOGY.exists()
assert FIXTURE.exists()
assert len(QUERIES) == 50, len(QUERIES)
ontology = ONTOLOGY.read_text()
fixture = FIXTURE.read_text()
assert "prov:" in ontology and "dqv:" in ontology and "odrl:" in ontology
assert "r68:actuationPerformed false" in fixture
assert "r68:run-complete" in fixture and "r68:run-stalled" in fixture
for query in QUERIES:
    text = query.read_text()
    assert "PREFIX r68:" in text, query
    assert "SELECT" in text.upper(), query
    assert "SERVICE" not in text.upper(), query
    assert "INSERT" not in text.upper(), query
    assert "DELETE" not in text.upper(), query
print(f"R68 contract PASS: {len(QUERIES)} sensors, public-semantic ontology, bounded fixture, zero SPARQL actuation")
