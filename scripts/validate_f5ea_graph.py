#!/usr/bin/env python3
"""validate_f5ea_graph.py -- SHACL-validate f5ea: solution-group graphs
against the fortune5-enterprise-architecture pack's canonical shapes file
(shapes/00-metamodel-hygiene.shacl.ttl, the DoD #9 metamodel-hygiene law).

This is the fortune5 sibling of scripts/validate_workgraphs.py (which
validates sjira WORKGRAPH/goal graphs against the semantic-jira pack
shapes). Where the workgraph validator checks work orders, this one checks
SolutionGroup individuals: closed shape, exactly-one groupKey, >= 1
groupsSBB, and no conflation with ea: SBB/ABB/ArchitectureContract types.

Usage:
    python3 scripts/validate_f5ea_graph.py                # full sweep
    python3 scripts/validate_f5ea_graph.py graph.ttl ...  # explicit graphs
    python3 scripts/validate_f5ea_graph.py --markdown     # report body too

Modes (default sweep runs the fixtures sweep + the TV-01 fiber):
    --fixtures   generate f5ea resource graphs from the pack's rendered
                 .tf fixtures (tests/fixtures/*_sbb.rendered.tf) via the
                 pack's scripts/gen_resource_graph.py, validate each.
    --tv-fiber   build the TV-01 conformance fiber (the real fixture graph
                 the conformance court runs over, including its SolutionGroup)
                 and validate it.
    plus any explicit .ttl paths are validated as-is.

Exit 0 = all conform; exit 1 = at least one graph has violations.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from pyshacl import validate
from rdflib import RDF, Graph, URIRef
from rdflib.namespace import SH

REPO = Path(__file__).resolve().parents[1]
PACK = REPO / "packs" / "fortune5-enterprise-architecture-pack"
SHAPES = PACK / "shapes" / "00-metamodel-hygiene.shacl.ttl"
ONTOLOGY = PACK / "ontology.ttl"
FIXTURES = PACK / "tests" / "fixtures"
TESTS = PACK / "tests"

F5 = "https://ggen.io/ontology/fortune5-enterprise-architecture#"
SHAPE_NODE = URIRef(F5 + "SolutionGroupShape")


def _import_tv_module():
    sys.path.insert(0, TESTS.as_posix())
    import test_conformance_vectors as tv  # type: ignore[reportMissingImports]  # noqa: E402
    return tv


def _load_shapes() -> Graph:
    shapes = Graph().parse(SHAPES.as_posix(), format="turtle")
    assert (SHAPE_NODE, RDF.type, SH.NodeShape) in shapes, (
        f"shapes file missing f5ea:SolutionGroupShape NodeShape")
    return shapes


def _merge_ontology(data: Graph) -> Graph:
    """Merge the pack ontology vocabulary so the AllDisjointClasses fence
    and sh:in members resolve."""
    merged = Graph()
    for t in data:
        merged.add(t)
    for t in Graph().parse(ONTOLOGY.as_posix(), format="turtle"):
        merged.add(t)
    return merged


def validate_graph(data: Graph, shapes: Graph):
    conforms, results_graph, _ = validate(
        data_graph=_merge_ontology(data),
        shacl_graph=shapes,
        ont_graph=None,
        inference="none",
        advanced=True,
    )
    if not isinstance(results_graph, Graph):
        # pyshacl returns a ValidationFailure when the shapes/data graphs
        # themselves are malformed -- surface it as a loud FAIL, never fall
        # through as a silent pass.
        raise RuntimeError(
            f"SHACL validation engine failure (malformed shapes or data): "
            f"{results_graph}")
    viols = []
    if not conforms:
        for t in results_graph.triples(
                (None, SH.focusNode, None)):
            focus = t[0]
            for m in results_graph.objects(focus, SH.resultMessage):
                viols.append((focus, str(m)))
    return bool(conforms), viols


def fixture_graphs():
    """Generate f5ea resource graphs from the pack's rendered .tf fixtures
    via the pack's own generator (real generator, real fixtures)."""
    gen = PACK / "scripts" / "gen_resource_graph.py"
    out = []
    for tf in sorted(FIXTURES.glob("*_sbb.rendered.tf")):
        provider = tf.name.split("_")[0]
        proc = subprocess.run(
            [sys.executable, gen.as_posix(), "--provider", provider,
             "--input", tf.as_posix()],
            capture_output=True, text=True, check=True,
        )
        g = Graph().parse(data=proc.stdout, format="turtle")
        out.append((f"fixture:{tf.name} -> resource graph", g))
    out.append(("fixture:ontology.ttl (vocabulary graph)",
                Graph().parse(ONTOLOGY.as_posix(), format="turtle")))
    out.append(("fixture:shapes file (self-validation)",
                Graph().parse(SHAPES.as_posix(), format="turtle")))
    return out


def tv_fiber_graph():
    real = _import_tv_module().synthesis_fiber()
    return "tv-fiber:TV-01 synthesis fiber", real


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="explicit .ttl graph files")
    ap.add_argument("--fixtures", action="store_true",
                    help="validate fixture-generated resource graphs")
    ap.add_argument("--tv-fiber", action="store_true",
                    help="validate the TV-01 conformance fiber graph")
    ap.add_argument("--markdown", action="store_true",
                    help="also print a markdown validation note")
    args = ap.parse_args()

    shapes = _load_shapes()
    targets = [(f"file:{p}", Graph().parse(p, format="turtle"))
               for p in args.files]
    if args.fixtures or not (args.files or args.tv_fiber):
        targets += fixture_graphs()
    if args.tv_fiber or not (args.files or args.fixtures):
        targets.append(tv_fiber_graph())

    any_fail = False
    rows = []
    for name, g in targets:
        conforms, viols = validate_graph(g, shapes)
        any_fail = any_fail or not conforms
        rows.append((name, conforms, viols))

    print("f5ea graph SHACL validation "
          "(shapes/00-metamodel-hygiene.shacl.ttl)")
    print()
    for name, conforms, viols in rows:
        verdict = "CONFORMS" if conforms else "VIOLATIONS"
        print(f"  {name}: {verdict} ({len(viols)} violations)")
        for focus, msg in viols:
            print(f"    - {focus}: {msg}")
    print()

    if args.markdown:
        print("## f5ea graph SHACL validation note")
        print()
        print("Command: `python3 scripts/validate_f5ea_graph.py` "
              "(shapes/00-metamodel-hygiene.shacl.ttl, DoD #9 law)")
        print()
        for name, conforms, viols in rows:
            print(f"- {name}: "
                  f"{'CONFORMS' if conforms else 'VIOLATIONS: ' + str(viols)}")
        print()

    if any_fail:
        print("RESULT: NOT CONFORMANT")
        return 1
    print("RESULT: ALL CONFORMANT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
