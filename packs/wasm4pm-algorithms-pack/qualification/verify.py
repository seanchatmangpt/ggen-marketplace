#!/usr/bin/env python3
"""Uniform court for wasm4pm-algorithms-pack (slimmed to vocabulary, 2026-10-01).

This pack declares the pi: vocabulary only; the 60 algorithm individuals are
owned by wasm4pm-facts-pack. Checks (exit 0 = ADMITTED, nonzero = REFUSED):
  1. Scoped: the pack graph alone is silent under every gates/*.rq
     (this pack owns no individuals, so zero rows is the expected scoped pass).
  2. Non-vacuity: pack graph + qualification/witness_fail.ttl fires >= 1 row
     under at least one gate; pack graph + qualification/witness_pass.ttl is
     silent under every gate (a conforming individual can pass).
  3. Join: pack graph + packs/wasm4pm-facts-pack/ontology.ttl is silent under
     every gate, resolves exactly 60 pi:ProcessIntelligenceAlgorithm
     individuals, the catalog template's SPARQL returns all 60 rows, and the
     dispatch/fidelity SPARQL (pi:verifiedAgainst) resolves exactly 1 row —
     the fact this pack contributed to the single owner (pi:Algo_ocel_dfg)
     actually resolves back through the join.

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
PREFIX pi: <https://wasm4pm.dev/pi#>
SELECT ?algorithm_id ?label ?doc ?citation ?category ?speed_tier ?quality_tier ?wasm_export ?cli_alias WHERE {
  ?a a pi:ProcessIntelligenceAlgorithm ;
     pi:algorithmId    ?algorithm_id ;
     pi:algorithmLabel ?label ;
     pi:algorithmDoc   ?doc ;
     pi:citation       ?citation ;
     pi:category       ?category ;
     pi:speedTier      ?speed_tier ;
     pi:qualityTier    ?quality_tier ;
     pi:wasmExport     ?wasm_export .
  OPTIONAL { ?a pi:cliAlias ?alias_raw . }
  BIND(COALESCE(?alias_raw, "") AS ?cli_alias)
} ORDER BY ?algorithm_id
"""

FIDELITY_QUERY = """
PREFIX pi: <https://wasm4pm.dev/pi#>
SELECT ?algorithm_id ?label ?wasm_export WHERE {
  ?a a pi:ProcessIntelligenceAlgorithm ;
     pi:algorithmId    ?algorithm_id ;
     pi:algorithmLabel ?label ;
     pi:wasmExport     ?wasm_export ;
     pi:verifiedAgainst ?note .
} ORDER BY ?algorithm_id
"""

COUNT_QUERY = """
PREFIX pi: <https://wasm4pm.dev/pi#>
SELECT (COUNT(DISTINCT ?a) AS ?n) WHERE { ?a a pi:ProcessIntelligenceAlgorithm . }
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
    fail_any_fire = False
    for gate in GATES:
        q = gate.read_text()
        pass_rows = rows_for([*pack_graph, PASS], q)
        fail_rows = rows_for([*pack_graph, FAIL], q)
        print(f"witness {gate.name}: pass_rows={len(pass_rows)} fail_rows={len(fail_rows)}")
        if pass_rows:
            failures.append(f"pass-witness-refused:{gate.name}:{pass_rows[0]}")
        if fail_rows:
            fail_any_fire = True
    if not fail_any_fire:
        failures.append("fail-witness-did-not-fire:any-gate")

    # 3: join with the single owner.
    for gate in GATES:
        q = gate.read_text()
        rows = rows_for([*pack_graph, FACTS], q)
        print(f"join {gate.name}: rows={len(rows)}")
        if rows:
            failures.append(f"join-refusal:{gate.name}:{rows[0]}")
    n = int(rows_for([*pack_graph, FACTS], COUNT_QUERY)[0][0])
    print(f"join individuals={n}")
    if n != 60:
        failures.append(f"join-count:{n}:expected=60")
    catalog = rows_for([*pack_graph, FACTS], CATALOG_QUERY)
    print(f"join catalog rows={len(catalog)}")
    if len(catalog) != 60:
        failures.append(f"join-catalog:{len(catalog)}:expected=60")
    fidelity = rows_for([*pack_graph, FACTS], FIDELITY_QUERY)
    print(f"join fidelity rows={len(fidelity)}: {[str(r[0]) for r in fidelity]}")
    if [str(r[0]) for r in fidelity] != ["ocel_dfg"]:
        failures.append("join-fidelity:pi:Algo_ocel_dfg-did-not-resolve-through-join")

    for f in failures:
        print(f"REFUSE {f}", file=sys.stderr)
    if failures:
        return 1
    print("ADMITTED wasm4pm-algorithms-pack: scoped silent, witnesses fire, join resolves 60 algorithms + 1 verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
