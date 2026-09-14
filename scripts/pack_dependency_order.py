#!/usr/bin/env python3
"""Real dependency-closed order + cycle detection for the ggen-marketplace.

Faithfully ported from a real, tested reference this session found by
surveying the ecosystem: /Users/sac/ex_noun_verb_cli's
ExNounVerbCli.CapabilityRegistry.dependency_order/1, itself a direct port of
the real Rust CapabilityRegistry::dependency_order
(~/clap-noun-verb/src/capability/registry.rs). Both are a real DFS-based
topological sort with explicit temporary/permanent marking (Tarjan's
depth-first classification for cycle detection), visiting node ids in
SORTED order for determinism (mirroring the Rust source's BTreeMap
iteration guarantee), refusing a missing dependency id and a real cycle
with the same typed-error shape as both reference implementations -- not a
from-scratch reimplementation, a faithful line-for-line algorithmic port.

Generic over any {id: [dependency_id, ...]} graph, so it works for:
- pack-compatibility-pack's own pc:dependsOnComponent facts (real today:
  reactor depends on spark, transcribed from ggen_igniter's mix.lock), and
- any future marketplace pack that declares real pack-to-pack dependencies.

Usage:
    python3 scripts/pack_dependency_order.py --from-ontology  # real ontology graph
    python3 scripts/pack_dependency_order.py --matrix         # print the graph
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY_PATH = REPO_ROOT / "packs" / "pack-compatibility-pack" / "ontology.ttl"

# Matches: pc:<Subject> a pc:Component ; pc:componentName "<name>" ; [pc:dependsOnComponent pc:<Object> .]
_COMPONENT_RE = re.compile(
    r"pc:(?P<subject>\w+)\s+a\s+pc:Component\s*;\s*"
    r'pc:componentName\s+"(?P<name>[^"]+)"\s*'
    r"(?:;\s*pc:dependsOnComponent\s+pc:(?P<dep_subject>\w+))?\s*\.",
    re.DOTALL,
)


class DependencyCycleError(Exception):
    """Raised with the exact node id the cycle was detected at -- mirrors
    both reference implementations' "Capability dependency cycle detected
    at: <id>" message shape."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        super().__init__(f"dependency cycle detected at: {node_id}")


class DependencyNotFoundError(Exception):
    """Raised when a node's declared dependency id isn't itself a known
    node -- mirrors "Capability dependency not found: <id>"."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        super().__init__(f"dependency not found: {node_id}")


def load_graph_from_ontology(ontology_path: Path = ONTOLOGY_PATH) -> dict[str, list[str]]:
    """Load the real pc:Component / pc:dependsOnComponent graph, keyed by
    componentName (the same lookup key scripts/check_pack_compatibility.py
    already uses), not the RDF subject IRI local name."""
    text = ontology_path.read_text()
    iri_to_name: dict[str, str] = {}
    iri_deps: dict[str, list[str]] = {}
    for m in _COMPONENT_RE.finditer(text):
        subject = m.group("subject")
        name = m.group("name")
        iri_to_name[subject] = name
        iri_deps.setdefault(subject, [])
        if m.group("dep_subject"):
            iri_deps[subject].append(m.group("dep_subject"))

    graph: dict[str, list[str]] = {}
    for iri, name in iri_to_name.items():
        deps = [iri_to_name.get(dep_iri, dep_iri) for dep_iri in iri_deps.get(iri, [])]
        graph[name] = deps
    return graph


def dependency_order(graph: dict[str, list[str]]) -> list[str]:
    """Returns a dependency-closed order (dependencies before dependents).

    Raises DependencyCycleError or DependencyNotFoundError on the first
    violation found, visiting ids in sorted order -- deterministic, never a
    silent partial result. Mirrors CapabilityRegistry.dependency_order/1
    exactly: temporary marks (on the current DFS path), permanent marks
    (fully resolved), post-order append on completion.
    """
    temporary: set[str] = set()
    permanent: set[str] = set()
    ordered: list[str] = []

    def visit(node_id: str) -> None:
        if node_id in permanent:
            return
        if node_id in temporary:
            raise DependencyCycleError(node_id)
        if node_id not in graph:
            raise DependencyNotFoundError(node_id)

        temporary.add(node_id)
        for dependency_id in graph[node_id]:
            visit(dependency_id)
        temporary.discard(node_id)
        permanent.add(node_id)
        ordered.append(node_id)

    for node_id in sorted(graph):
        visit(node_id)

    return ordered


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--from-ontology", action="store_true", help="compute order over the real ontology graph")
    parser.add_argument("--matrix", action="store_true", help="print the real ontology graph and exit")
    args = parser.parse_args(argv)

    graph = load_graph_from_ontology()

    if args.matrix or not args.from_ontology:
        for node_id in sorted(graph):
            deps = graph[node_id]
            print(f"{node_id}: depends on {deps if deps else '(none)'}")
        if not args.from_ontology:
            return 0

    try:
        order = dependency_order(graph)
    except (DependencyCycleError, DependencyNotFoundError) as e:
        code = "CYCLE" if isinstance(e, DependencyCycleError) else "MISSING_DEPENDENCY"
        print(f"REFUSED:{code}:{e.node_id}", file=sys.stderr)
        return 1

    print("order: " + " -> ".join(order))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
