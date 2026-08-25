#!/usr/bin/env python3
"""R67 consumer-independence court.

HANDWRITTEN_IRREDUCIBLE_REASON: bounded RDFLib SPARQL execution adapter only;
reusable measurement semantics remain RDF/SPARQL-owned.
"""
from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "r67-consumer-independence-current.ttl"
ONTOLOGY = ROOT / "ontology" / "r67-consumer-independence.ttl"
QUERY_NAMES = [f"{n}_" for n in range(651, 701)]


def scalar(rows, name):
    assert len(rows) == 1, (name, rows)
    return int(rows[0][0])


def main():
    graph = Graph()
    graph.parse(ROOT / "ontology.ttl", format="turtle")
    graph.parse(ONTOLOGY, format="turtle")
    graph.parse(FIXTURE, format="turtle")

    paths = []
    for prefix in QUERY_NAMES:
        matches = sorted((ROOT / "queries").glob(prefix + "*.rq"))
        assert len(matches) == 1, (prefix, [p.name for p in matches])
        paths.append(matches[0])
    assert len(paths) == 50

    results = {}
    for path in paths:
        rows = list(graph.query(path.read_text()))
        results[path.name] = rows
        print(f"PASS {path.name} rows={len(rows)}")

    assert scalar(results[paths[0].name], paths[0].name) == 4
    by_number = {int(path.name.split('_', 1)[0]): results[path.name] for path in paths}
    assert scalar(by_number[652], "652") == 4
    assert scalar(by_number[653], "653") == 3
    assert scalar(by_number[654], "654") == 3
    assert scalar(by_number[655], "655") == 4
    assert scalar(by_number[656], "656") == 4
    assert scalar(by_number[657], "657") == 4
    assert scalar(by_number[658], "658") == 4
    assert scalar(by_number[659], "659") == 4
    assert scalar(by_number[660], "660") == 3
    assert scalar(by_number[661], "661") == 1
    assert scalar(by_number[662], "662") == 4
    assert scalar(by_number[663], "663") == 4
    assert scalar(by_number[673], "673") == 1
    assert scalar(by_number[674], "674") == 3
    assert scalar(by_number[686], "686") == 5
    assert scalar(by_number[687], "687") == 1
    assert scalar(by_number[688], "688") == 1
    assert scalar(by_number[689], "689") == 0
    assert scalar(by_number[690], "690") == 0
    assert scalar(by_number[691], "691") == 0
    assert scalar(by_number[692], "692") == 0
    assert scalar(by_number[693], "693") == 0
    assert scalar(by_number[694], "694") == 1
    assert scalar(by_number[695], "695") == 1
    assert len(by_number[699]) == 1
    assert len(by_number[700]) == 4
    print("R67_CONSUMER_INDEPENDENCE=50 ALIVE profiles=4 fully_orthogonal_pairs=5 strong_orthogonal_pairs=1 consequential_do=false")


if __name__ == "__main__":
    main()
