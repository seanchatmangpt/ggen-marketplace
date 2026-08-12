#!/usr/bin/env python3
"""Cross-reference dsrust-pack's live admission gate against its exact-source ledger."""
from __future__ import annotations

import re
from pathlib import Path

import rdflib

ROOT = Path(__file__).resolve().parent.parent
GATE = ROOT / "gates" / "010_admission.rq"
EVIDENCE = ROOT / "evidence" / "dsrust-source-coverage.ttl"
QUERY = ROOT / "queries" / "coverage_cross_reference.rq"


def _quoted_values(group: str) -> set[str]:
    return set(re.findall(r'"([A-Za-z0-9_]+)"', group))


def admitted_from_gate(text: str) -> dict[str, set[str]]:
    module = re.search(
        r'dsrust:Module\s*;\s*dsrust:kind\s+\?value\s*\.\s*FILTER\(\?value\s+NOT\s+IN\s*\(([^)]+)\)\)',
        text,
        re.S,
    )
    optimizer = re.search(
        r'dsrust:Optimizer\s*;\s*dsrust:kind\s+\?value\s*\.\s*FILTER\(\?value\s+NOT\s+IN\s*\(([^)]+)\)\)',
        text,
        re.S,
    )
    if not module or not optimizer:
        raise AssertionError("live gate kind lists not found; update coverage parser with gate shape")
    return {"Module": _quoted_values(module.group(1)), "Optimizer": _quoted_values(optimizer.group(1))}


def admitted_from_ledger(graph: rdflib.Graph) -> dict[str, set[str]]:
    rows = graph.query(
        """
        PREFIX audit: <http://seanchatmangpt.github.io/packs/dsrust/audit#>
        SELECT ?role ?symbol WHERE {
          ?entry a audit:Kind ; audit:role ?role ; audit:symbol ?symbol ; audit:admitted true .
        }
        """
    )
    out = {"Module": set(), "Optimizer": set()}
    for row in rows:
        out[str(row.role)].add(str(row.symbol))
    return out


def main() -> int:
    live = admitted_from_gate(GATE.read_text(encoding="utf-8"))
    graph = rdflib.Graph()
    graph.parse(EVIDENCE, format="turtle")
    ledger = admitted_from_ledger(graph)
    if live != ledger:
        raise SystemExit(f"REFUSED:DSRUST_COVERAGE_DRIFT:gate={live}:ledger={ledger}")

    rows = list(graph.query(QUERY.read_text(encoding="utf-8")))
    admitted = sum(str(row.admitted).lower() == "true" for row in rows)
    print(f"OK dsrust source coverage: admitted={admitted} total={len(rows)} source=f24adde08c1d8850e4d7079d019643bb40f905cb")
    for row in rows:
        mark = "ADMITTED" if str(row.admitted).lower() == "true" else "EXCLUDED"
        print(f"{row.role}\t{mark}\t{row.symbol}\t{row.sourceFile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
