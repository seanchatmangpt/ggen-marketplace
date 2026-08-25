from pathlib import Path
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

ROOT = Path(__file__).resolve().parents[1]
g = Graph()
g.parse(ROOT / "ontology.ttl", format="turtle")
g.parse(ROOT / "fixtures/reference.ttl", format="turtle")

queries = sorted((ROOT / "queries").glob("*.sparql"))
assert queries, "R70 must expose executable capital-yield courts"
for path in queries:
    text = path.read_text()
    prepareQuery(text)
    rows = list(g.query(text))
    assert rows, f"{path.name} must observe its admitted metric"

assert len(queries) >= 50, f"R70 requires >=50 independent courts, got {len(queries)}"
fixture = (ROOT / "fixtures/reference.ttl").read_text()
assert "acy:handEditedGeneratedCount 0" in fixture
assert "acy:authorityViolationCount 0" in fixture
assert "acy:actuationPerformed false" in fixture
print(f"R70_AUTOCATALYTIC_CAPITAL_YIELD=ALIVE courts={len(queries)}")
