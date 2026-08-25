from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]

g = Graph()
g.parse(ROOT / "ontology.ttl")
g.parse(ROOT / "fixtures" / "r71-portfolio.ttl")
queries = sorted((ROOT / "queries").glob("*.rq"))
assert len(queries) == 51, len(queries)
results = {}
for path in queries:
    rows = list(g.query(path.read_text()))
    results[path.name] = rows

assert len(results["001_candidate_census.rq"]) == 5
assert len(results["035_clean_independent_frontier.rq"]) == 3
assert len(results["046_orthogonal_pair_frontier.rq"]) >= 2
assert len(results["050_next_consumer_crown.rq"]) == 3
assert len(results["051_manufacturing_plan_projection.rq"]) == 3
assert len(results["031_ambient_do_falsifier.rq"]) == 1
assert len(results["032_correlated_root_falsifier.rq"]) == 2
assert len(results["033_stale_candidate_falsifier.rq"]) == 1
shortfall = int(results["049_ten_consumer_shortfall.rq"][0][0])
assert shortfall == 7, shortfall
print(f"R71_COURTS=51 CLEAN_INDEPENDENT=3 TEN_X_SHORTFALL={shortfall} CONSEQUENTIAL_DO=false")
