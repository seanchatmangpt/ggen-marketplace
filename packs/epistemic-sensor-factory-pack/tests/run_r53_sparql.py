#!/usr/bin/env python3
from pathlib import Path
from rdflib import Graph

root = Path(__file__).resolve().parents[1]
g = Graph().parse(root / "fixtures/r53-closed-loop-consumer-assimilation.ttl", format="turtle")
queries = sorted(p for p in (root / "queries").glob("*.rq") if 451 <= int(p.name.split("_")[0]) <= 500)
assert len(queries) == 50, f"expected 50 R53 sensors, got {len(queries)}"
rows = {}
for path in queries:
    result = list(g.query(path.read_text()))
    rows[int(path.name.split("_")[0])] = result
    print(f"R53_SENSOR_{path.name}=PASS rows={len(result)}")
assert int(rows[451][0][0]) == 1
assert rows[458] == []
assert rows[460] == []
assert rows[475] == []
assert int(rows[476][0][0]) == 1
assert int(rows[477][0][0]) == 1
assert len(rows[480]) == 1
assert int(rows[486][0][0]) == 3
assert rows[487] == []
assert rows[490] == []
assert [int(r[1]) for r in rows[491]] == [1, 2, 3]
assert int(rows[493][0][1]) == 3
assert int(rows[496][0][0]) == 3
assert rows[497] == []
assert rows[498] == []
assert int(rows[500][0][0]) == 3
assert int(rows[500][0][1]) == 997
print("R53_CLOSED_LOOP_SPARQL=ALIVE")
