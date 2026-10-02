#!/usr/bin/env python3
"""Uniform court for wasm4pm-cognition-pack (slimmed to vocabulary, 2026-10-01).

This pack declares the compat: vocabulary only; the 55 breed individuals are
owned by wasm4pm-facts-pack. Checks (exit 0 = ADMITTED, nonzero = REFUSED):
  1. Scoped: the pack graph alone is silent under every gates/*.rq
     (this pack owns no individuals, so zero rows is the expected scoped pass).
  2. Non-vacuity: pack graph + qualification/witness_fail.ttl fires >= 1 row
     under at least one gate; pack graph + qualification/witness_pass.ttl is
     silent under every gate (a conforming individual can pass).
  3. Join: pack graph + packs/wasm4pm-facts-pack/ontology.ttl is silent under
     every gate, resolves exactly 55 compat:CognitionBreed individuals across
     13 breedFamily values, and the catalog template's SPARQL returns all 55
     rows (the IRI-literal consumer join actually resolves).

Stdlib + rdflib only; no network, no subprocess, no actuation.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from rdflib import Graph
except ImportError as exc:  # pragma: no cover
    raise SystemExit("REFUSED:VERIFIER_UNAVAILABLE:rdflib") from exc

ROOT = Path(__file__).resolve().parents[1]
GATES = sorted((ROOT / "gates").glob("*.rq"), key=lambda p: p.name)
PASS = ROOT / "qualification" / "witness_pass.ttl"
FAIL = ROOT / "qualification" / "witness_fail.ttl"
FACTS = ROOT.parent / "wasm4pm-facts-pack" / "ontology.ttl"

CATALOG_QUERY = """
PREFIX compat: <https://wasm4pm.dev/ns#>
SELECT ?breed_id ?breed_label ?breed_doc ?citation ?breed_family WHERE {
  ?b a compat:CognitionBreed ;
     compat:breedId ?breed_id ;
     compat:breedLabel ?breed_label ;
     compat:breedDoc ?breed_doc ;
     compat:citation ?citation ;
     compat:breedFamily ?breed_family .
} ORDER BY ?breed_id
"""

FAMILY_QUERY = """
PREFIX compat: <https://wasm4pm.dev/ns#>
SELECT (COUNT(DISTINCT ?b) AS ?n) (COUNT(DISTINCT ?f) AS ?fams) WHERE {
  ?b a compat:CognitionBreed ; compat:breedFamily ?f .
}
"""


def rows_for(paths, query):
    g = Graph()
    for p in paths:
        g.parse(p, format="turtle")
    return list(g.query(query))


def main() -> int:
    failures: list[str] = []
    pack_graph = [ROOT / "ontology.ttl"]

    # 1: scoped silence.
    for gate in GATES:
        q = gate.read_text()
        rows = rows_for(pack_graph, q)
        print(f"scoped {gate.name}: rows={len(rows)}")
        if rows:
            failures.append(f"scoped-refusal:{gate.name}:{rows[0]}")

    # 2: witnesses.
    pass_any_fire = False
    for gate in GATES:
        q = gate.read_text()
        pass_rows = rows_for([*pack_graph, PASS], q)
        fail_rows = rows_for([*pack_graph, FAIL], q)
        print(f"witness {gate.name}: pass_rows={len(pass_rows)} fail_rows={len(fail_rows)}")
        if pass_rows:
            failures.append(f"pass-witness-refused:{gate.name}:{pass_rows[0]}")
        if fail_rows:
            pass_any_fire = True
    if not pass_any_fire:
        failures.append("fail-witness-did-not-fire:any-gate")

    # 3: join with the single owner.
    for gate in GATES:
        q = gate.read_text()
        rows = rows_for([*pack_graph, FACTS], q)
        print(f"join {gate.name}: rows={len(rows)}")
        if rows:
            failures.append(f"join-refusal:{gate.name}:{rows[0]}")
    count = rows_for([*pack_graph, FACTS], FAMILY_QUERY)[0]
    n, fams = int(count[0]), int(count[1])
    print(f"join individuals={n} families={fams}")
    if n != 55 or fams != 13:
        failures.append(f"join-count:{n}breeds/{fams}families:expected=55/13")
    catalog = rows_for([*pack_graph, FACTS], CATALOG_QUERY)
    print(f"join catalog rows={len(catalog)}")
    if len(catalog) != 55:
        failures.append(f"join-catalog:{len(catalog)}:expected=55")

    for f in failures:
        print(f"REFUSE {f}", file=sys.stderr)
    if failures:
        return 1
    print("ADMITTED wasm4pm-cognition-pack: scoped silent, witnesses fire, join resolves 55 breeds / 13 families")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
