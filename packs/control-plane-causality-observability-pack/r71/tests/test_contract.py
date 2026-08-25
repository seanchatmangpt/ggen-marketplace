from pathlib import Path
from rdflib import Graph

root = Path(__file__).resolve().parents[1]
g = Graph()
g.parse(root / "ontology.ttl")
g.parse(root / "fixtures/live-evidence.ttl")
queries = sorted((root / "queries").glob("*.sparql"))
assert len(queries) == 50, len(queries)
for query in queries:
    list(g.query(query.read_text()))
assert len(list(g.query((root / "queries/003_missing_receipt.sparql").read_text()))) == 1
assert len(list(g.query((root / "queries/035_false_1000x_claim.sparql").read_text()))) == 0
assert len(list(g.query((root / "queries/036_1000x_candidate.sparql").read_text()))) == 0
assert len(list(g.query((root / "queries/050_clean_assimilation_crown.sparql").read_text()))) == 2
print("R71_CAUSAL_EVIDENCE_ASSIMILATION=PASS queries=50 clean=2 thousand_x=NOT_ADMITTED")
