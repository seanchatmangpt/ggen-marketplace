#!/usr/bin/env python3
"""Uniform court for gym-mcp-surface-pack (kernel + family modules).

Checks, in order (exit 0 = ADMITTED, nonzero = REFUSED):
  1. Kernel self-description graph: gates/010_mcp_authority_boundary.rq silent.
  2. Each family module (ontology/*.ttl, excluding the kernel root ontology.ttl):
     the same gate silent — proves the module graphs render standalone.
  3. Every witnesses/fail/*.ttl: the gate fires (>= 1 row) — anti-vacuity.
  4. Union guard: kernel + ggen-ecosystem module together MUST fire
     (multiple-mcp-server-nodes-refused) — the one-server-per-graph rendering
     contract is live, not decorative.

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
GATE = ROOT / "gates" / "010_mcp_authority_boundary.rq"
UNION_GUARD_PAIR = (ROOT / "ontology.ttl", ROOT / "ontology" / "ggen-ecosystem.ttl")


def gate_rows(graph_path: Path, query: str) -> list:
    g = Graph()
    g.parse(graph_path, format="turtle")
    return list(g.query(query))


def main() -> int:
    query = GATE.read_text()
    failures: list[str] = []

    # 1 + 2: silent graphs (kernel root + each family module).
    silent = [ROOT / "ontology.ttl"] + sorted(
        p for p in (ROOT / "ontology").glob("*.ttl")
    )
    for path in silent:
        rows = gate_rows(path, query)
        print(f"silent-check {path.relative_to(ROOT)}: rows={len(rows)}")
        if rows:
            failures.append(f"unexpected-refusal:{path.name}:{rows[0][1]}")

    # 3: fail witnesses must fire.
    for path in sorted((ROOT / "witnesses" / "fail").glob("*.ttl")):
        rows = gate_rows(path, query)
        print(f"fire-check witnesses/fail/{path.name}: rows={len(rows)}")
        if not rows:
            failures.append(f"witness-did-not-fire:{path.name}")

    # 4: union guard must fire.
    g = Graph()
    for p in UNION_GUARD_PAIR:
        g.parse(p, format="turtle")
    union_rows = list(g.query(query))
    print(f"union-guard kernel+ggen-ecosystem: rows={len(union_rows)}")
    if not any(str(r[1]) == "multiple-mcp-server-nodes-refused" for r in union_rows):
        failures.append("union-guard-inert:merging-kernel-and-module-did-not-refuse")

    for f in failures:
        print(f"REFUSE {f}", file=sys.stderr)
    if failures:
        return 1
    print("ADMITTED gym-mcp-surface-pack: kernel + modules silent, witnesses fire, union guard fires")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
