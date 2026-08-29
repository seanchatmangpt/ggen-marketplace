from pathlib import Path
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

ROOT = Path(__file__).resolve().parents[1]
g = Graph()
g.parse(ROOT / "ontology.ttl", format="turtle")
g.parse(ROOT / "fixtures/reference.ttl", format="turtle")

queries = sorted((ROOT / "queries").glob("*.sparql"))
assert len(queries) >= 50, f"R71 requires >=50 independent selection courts, got {len(queries)}"
for path in queries:
    prepareQuery(path.read_text())
    rows = list(g.query(path.read_text()))
    assert rows, f"{path.name} must observe its selection dimension"
fixture = (ROOT / "fixtures/reference.ttl").read_text()
assert "mca:selected true" in fixture
assert "mca:actuationPerformed false" in fixture
print(f"R71_MARGINAL_CAPITAL_ALLOCATOR=ALIVE courts={len(queries)} authority=SELECT_ONLY")
