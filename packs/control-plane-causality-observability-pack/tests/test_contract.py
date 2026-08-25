from pathlib import Path
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

ROOT = Path(__file__).resolve().parents[1]
queries = sorted((ROOT / "queries").glob("*.sparql"))
assert len(queries) >= 100, len(queries)
required = {f"{n:03d}" for n in range(1, 101)}
present = {p.name[:3] for p in queries}
assert required <= present, sorted(required - present)

g = Graph()
g.parse(ROOT / "ontology.ttl", format="turtle")
g.parse(ROOT / "fixtures/reference.ttl", format="turtle")
assert len(g) > 75

for path in queries:
    prepareQuery(path.read_text())
    list(g.query(path.read_text()))

unrelated = list(g.query((ROOT / "queries/009_unrelated_workflow_fanout.sparql").read_text()))
stale = list(g.query((ROOT / "queries/005_stale_running_memory.sparql").read_text()))
clean_control = list(g.query((ROOT / "queries/050_clean_causal_chain.sparql").read_text()))
clean_yield = list(g.query((ROOT / "queries/093_clean_causal_yield_chain.sparql").read_text()))
causal_y = list(g.query((ROOT / "queries/099_causally_grounded_yield_frontier.sparql").read_text()))
phase_change = list(g.query((ROOT / "queries/100_phase_change_crown.sparql").read_text()))
thousand_x = list(g.query((ROOT / "queries/083_1000x_admission_crown.sparql").read_text()))
assert unrelated, "fixture must falsify unrelated workflow fanout"
assert stale, "fixture must expose stale RUNNING memory"
assert clean_control, "fixture must preserve a clean request-workflow-receipt chain"
assert clean_yield, "fixture must preserve a clean primitive-consumer-action causal chain"
assert causal_y, "fixture must expose positive causally grounded Y"
assert phase_change, "fixture must expose positive evidence-bounded Y and M"
assert not thousand_x, "1000X must remain NOT_ADMITTED while any factor is below 10"
assert 'consequential_do = "BRCE_ONLY"' in (ROOT / "pack.toml").read_text()
assert "cpc:actuationPerformed false" in (ROOT / "fixtures/reference.ttl").read_text()
print(
    f"ALIVE sensors={len(queries)} triples={len(g)} unrelated={len(unrelated)} "
    f"stale_running={len(stale)} clean_control={len(clean_control)} "
    f"clean_yield={len(clean_yield)} causal_y={len(causal_y)} "
    f"phase_change={len(phase_change)} thousand_x={len(thousand_x)}"
)
