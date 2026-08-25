#!/usr/bin/env python3
"""R54/R66 consumer-independence court.

HANDWRITTEN_IRREDUCIBLE_REASON: bounded RDFLib SPARQL execution adapter only;
reusable measurement semantics remain RDF/SPARQL-owned.
"""
from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "r54-consumer-independence-current.ttl"
R54_ONTOLOGY = ROOT / "ontology" / "r54-consumer-independence.ttl"
QUERY_NAMES = [f"{n}_" for n in range(651, 701)]


def main():
    graph = Graph()
    graph.parse(ROOT / "ontology.ttl", format="turtle")
    graph.parse(R54_ONTOLOGY, format="turtle")
    graph.parse(FIXTURE, format="turtle")

    paths = []
    for prefix in QUERY_NAMES:
        matches = sorted((ROOT / "queries").glob(f"{prefix}*.rq"))
        assert len(matches) == 1, (prefix, [p.name for p in matches])
        paths.append(matches[0])
    assert len(paths) == 50

    results = {}
    for path in paths:
        rows = list(graph.query(path.read_text()))
        results[path.name] = rows
        print(f"PASS {path.name} rows={len(rows)}")

    def scalar(number):
        name = next(name for name in results if name.startswith(f"{number}_"))
        rows = results[name]
        assert len(rows) == 1, (name, rows)
        return int(rows[0][0])

    assert scalar(651) == 4
    assert scalar(652) == 4
    assert scalar(653) == 3
    assert scalar(654) == 3
    assert scalar(655) == 4
    assert scalar(656) == 4
    assert scalar(657) == 4
    assert scalar(658) == 4
    assert scalar(659) == 4
    assert scalar(660) == 3
    assert scalar(661) == 1
    assert scalar(662) == 4
    assert scalar(663) == 4
    assert scalar(673) == 1
    assert scalar(674) == 3
    assert scalar(687) == 1
    assert scalar(688) == 1
    assert scalar(689) == 0
    assert scalar(690) == 0
    assert scalar(691) == 0
    assert scalar(692) == 0
    assert scalar(693) == 0
    assert scalar(694) == 1
    assert len(next(rows for name, rows in results.items() if name.startswith("699_"))) == 1
    assert len(next(rows for name, rows in results.items() if name.startswith("700_"))) == 4

    print(f"R66_CONSUMER_INDEPENDENCE=50 ALIVE profiles=4 triples={len(graph)} consequential_do=false")


if __name__ == "__main__":
    main()
