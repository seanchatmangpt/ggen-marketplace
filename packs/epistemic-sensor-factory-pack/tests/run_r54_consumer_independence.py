#!/usr/bin/env python3
"""R54 consumer-independence court.

HANDWRITTEN_IRREDUCIBLE_REASON: bounded RDFLib SPARQL execution adapter only;
reusable measurement semantics remain RDF/SPARQL-owned.
"""
from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "r54-consumer-independence-current.ttl"
R54_ONTOLOGY = ROOT / "ontology" / "r54-consumer-independence.ttl"


def scalar(results, name):
    rows = results[name]
    assert len(rows) == 1, (name, rows)
    return int(rows[0][0])


def main():
    graph = Graph()
    graph.parse(ROOT / "ontology.ttl", format="turtle")
    graph.parse(R54_ONTOLOGY, format="turtle")
    graph.parse(FIXTURE, format="turtle")

    queries = []
    for path in sorted((ROOT / "queries").glob("*.rq")):
        prefix = path.name.split("_", 1)[0]
        if prefix.isdigit() and 651 <= int(prefix) <= 700:
            queries.append(path)
    assert len(queries) == 50, len(queries)

    results = {}
    for path in queries:
        rows = list(graph.query(path.read_text()))
        results[path.name] = rows
        print(f"PASS {path.name} rows={len(rows)}")

    assert scalar(results, "651_independence_profile_count.rq") == 4
    assert scalar(results, "652_distinct_repository_count.rq") == 4
    assert scalar(results, "653_runtime_family_diversity.rq") == 3
    assert scalar(results, "654_language_family_diversity.rq") == 3
    assert scalar(results, "655_execution_kernel_diversity.rq") == 4
    assert scalar(results, "656_failure_domain_diversity.rq") == 4
    assert scalar(results, "657_authority_domain_diversity.rq") == 4
    assert scalar(results, "658_receipt_protocol_diversity.rq") == 4
    assert scalar(results, "659_qualification_family_diversity.rq") == 4
    assert scalar(results, "660_ontology_profile_diversity.rq") == 3
    assert scalar(results, "661_hosting_plane_diversity.rq") == 1
    assert scalar(results, "662_consumer_family_diversity.rq") == 4
    assert scalar(results, "663_exact_head_parity_count.rq") == 4
    assert scalar(results, "673_admitted_consumer_count.rq") == 1
    assert scalar(results, "674_partial_consumer_count.rq") == 3
    assert scalar(results, "686_fully_orthogonal_pair_count.rq") == 5
    assert scalar(results, "687_same_runtime_pair_count.rq") == 1
    assert scalar(results, "688_same_language_pair_count.rq") == 1
    assert scalar(results, "689_same_kernel_pair_count.rq") == 0
    assert scalar(results, "690_same_failure_domain_pair_count.rq") == 0
    assert scalar(results, "691_same_authority_domain_pair_count.rq") == 0
    assert scalar(results, "692_same_receipt_protocol_pair_count.rq") == 0
    assert scalar(results, "693_same_qualification_family_pair_count.rq") == 0
    assert scalar(results, "694_same_ontology_profile_pair_count.rq") == 1
    assert scalar(results, "695_strong_orthogonal_pair_count.rq") == 1
    assert len(results["699_prioritized_independent_candidate.rq"]) == 1
    assert len(results["700_clean_independence_frontier.rq"]) == 4

    print("R54_CONSUMER_INDEPENDENCE=50 ALIVE profiles=4 fully_orthogonal_pairs=5 strong_orthogonal_pairs=1")


if __name__ == "__main__":
    main()
