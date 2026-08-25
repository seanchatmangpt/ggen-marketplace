from pathlib import Path
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

ROOT = Path(__file__).resolve().parents[1]
queries = sorted((ROOT / "queries").glob("*.sparql"))
assert len(queries) == 50, len(queries)
assert [p.name[:3] for p in queries] == [f"{n:03d}" for n in range(1, 51)]

g = Graph()
g.parse(ROOT / "ontology.ttl", format="turtle")
g.parse(ROOT / "fixtures/reference.ttl", format="turtle")
assert len(g) > 25

for path in queries:
    prepareQuery(path.read_text())
    list(g.query(path.read_text()))

unrelated = list(g.query((ROOT / "queries/009_unrelated_workflow_fanout.sparql").read_text()))
stale = list(g.query((ROOT / "queries/005_stale_running_memory.sparql").read_text()))
clean = list(g.query((ROOT / "queries/050_clean_causal_chain.sparql").read_text()))
assert unrelated, "fixture must falsify unrelated workflow fanout"
assert stale, "fixture must expose stale RUNNING memory"
assert clean, "fixture must preserve a clean causal chain"
assert 'consequential_do = "BRCE_ONLY"' in (ROOT / "pack.toml").read_text()
assert "cpc:actuationPerformed false" in (ROOT / "fixtures/reference.ttl").read_text()
print(f"ALIVE sensors={len(queries)} triples={len(g)} unrelated={len(unrelated)} stale_running={len(stale)} clean={len(clean)}")
