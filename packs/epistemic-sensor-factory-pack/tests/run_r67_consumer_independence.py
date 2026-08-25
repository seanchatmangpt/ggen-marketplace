#!/usr/bin/env python3
"""R67 consumer-independence court.

HANDWRITTEN_IRREDUCIBLE_REASON: bounded RDFLib SPARQL execution adapter only;
reusable measurement semantics remain RDF/SPARQL-owned.

Marketplace sensor families may lawfully reuse numeric ordinals. This court binds
its exact semantic query identities rather than assuming global ordinal uniqueness.
"""
from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "r67-consumer-independence-current.ttl"
ONTOLOGY = ROOT / "ontology" / "r67-consumer-independence.ttl"
QUERY_NAMES = [
    "651_independence_profile_count.rq",
    "652_distinct_repository_count.rq",
    "653_runtime_family_diversity.rq",
    "654_language_family_diversity.rq",
    "655_execution_kernel_diversity.rq",
    "656_failure_domain_diversity.rq",
    "657_authority_domain_diversity.rq",
    "658_receipt_protocol_diversity.rq",
    "659_qualification_family_diversity.rq",
    "660_ontology_profile_diversity.rq",
    "661_hosting_plane_diversity.rq",
    "662_consumer_family_diversity.rq",
    "663_exact_head_parity_count.rq",
    "664_identity_verified_count.rq",
    "665_authority_bounded_count.rq",
    "666_court_reusable_count.rq",
    "667_receipt_return_capable_count.rq",
    "668_public_ontology_aligned_count.rq",
    "669_ggen_manufacturable_count.rq",
    "670_replay_capable_count.rq",
    "671_dependency_closed_count.rq",
    "672_no_ambient_do_count.rq",
    "673_admitted_consumer_count.rq",
    "674_partial_consumer_count.rq",
    "675_admitted_runtime_diversity.rq",
    "676_admitted_failure_domain_diversity.rq",
    "677_admitted_authority_domain_diversity.rq",
    "678_admitted_receipt_protocol_diversity.rq",
    "679_admitted_qualification_family_diversity.rq",
    "680_admitted_ontology_profile_diversity.rq",
    "681_strong_ready_language_diversity.rq",
    "682_strong_ready_kernel_diversity.rq",
    "683_strong_ready_failure_domain_diversity.rq",
    "684_strong_ready_receipt_protocol_diversity.rq",
    "685_strong_ready_qualification_diversity.rq",
    "686_fully_orthogonal_pair_count.rq",
    "687_same_runtime_pair_count.rq",
    "688_same_language_pair_count.rq",
    "689_same_kernel_pair_count.rq",
    "690_same_failure_domain_pair_count.rq",
    "691_same_authority_domain_pair_count.rq",
    "692_same_receipt_protocol_pair_count.rq",
    "693_same_qualification_family_pair_count.rq",
    "694_same_ontology_profile_pair_count.rq",
    "695_strong_orthogonal_pair_count.rq",
    "696_readiness_by_runtime.rq",
    "697_readiness_by_failure_domain.rq",
    "698_readiness_by_authority_domain.rq",
    "699_prioritized_independent_candidate.rq",
    "700_clean_independence_frontier.rq",
]


def scalar(rows, name):
    assert len(rows) == 1, (name, rows)
    return int(rows[0][0])


def main():
    graph = Graph()
    graph.parse(ROOT / "ontology.ttl", format="turtle")
    graph.parse(ONTOLOGY, format="turtle")
    graph.parse(FIXTURE, format="turtle")

    assert len(QUERY_NAMES) == 50
    paths = [ROOT / "queries" / name for name in QUERY_NAMES]
    missing = [path.name for path in paths if not path.is_file()]
    assert not missing, missing
    assert len({path.name for path in paths}) == 50

    results = {}
    for path in paths:
        rows = list(graph.query(path.read_text()))
        results[path.name] = rows
        print(f"PASS {path.name} rows={len(rows)}")

    by_number = {int(path.name.split('_', 1)[0]): results[path.name] for path in paths}
    assert scalar(by_number[651], "651") == 4
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
