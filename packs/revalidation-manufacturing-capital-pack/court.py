#!/usr/bin/env python3
"""R73 bounded reference court.

HANDWRITTEN_IRREDUCIBLE_REASON: this file is verifier/runtime substrate that parses and executes
public RDF/SPARQL semantics; it does not encode reusable domain truth and has no actuation authority.
"""
from pathlib import Path
from rdflib import Graph
from rdflib.plugins.sparql.parser import parseQuery

ROOT = Path(__file__).resolve().parent

graph = Graph()
graph.parse(ROOT / "ontology.ttl", format="turtle")
graph.parse(ROOT / "fixture.ttl", format="turtle")
queries = sorted((ROOT / "queries").glob("*.rq"))
assert len(queries) >= 51, f"expected at least 51 R73 courts, got {len(queries)}"

results = {}
for query_path in queries:
    text = query_path.read_text()
    parseQuery(text)
    results[query_path.name] = list(graph.query(text))

assert results["001-stale-head-revalidation.rq"], "stale-head falsifier must observe grounded stale memory"
assert results["021-zero-ambient-do.rq"] == [], "ambient consequential DO must remain empty"
assert results["048-revalidation-manufacturing-frontier.rq"], "clean manufacturing frontier must be non-empty"
assert results["049-1000x-admission-falsifier.rq"], "fixture must refuse unsupported 1000X crown"
assert results["050-capital-allocation-crown.rq"], "capital-allocation crown must select evidence-bounded candidates"
assert results["051-manufacturing-plan-projection.rq"], "deterministic manufacturing projection must be non-empty"

print(f"R73_ALIVE courts={len(queries)} triples={len(graph)}")
