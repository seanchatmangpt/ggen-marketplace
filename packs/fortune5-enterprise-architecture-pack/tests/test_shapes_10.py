# tests/test_shapes_10.py — court for shapes/10-sbb-realization.shacl.ttl
# (dissertation §9.1: rho(S) = A enforcement).
#
# Court: the shape file must (a) parse as Turtle, (b) pyshacl-flag a dangling
# SBB (ea:satisfiesABB pointing at a non-ABB node) — the mutation, and
# (c) accept a clean SBB whose satisfiesABB lands on a typed ABB.
#
# Real files, real pyshacl — no mocks (Chicago discipline).

from pathlib import Path

from rdflib import Graph, RDF, URIRef
from pyshacl import validate

PACK_DIR = Path(__file__).resolve().parents[1]
SHAPES_FILE = PACK_DIR / "shapes" / "10-sbb-realization.shacl.ttl"

F5 = "https://ggen.io/ontology/fortune5-enterprise-architecture#"
EA = "https://chatman.ai/ontology/enterprise-architecture#"
SH = "http://www.w3.org/ns/shacl#"


def _validate_fixture(fixture_ttl: str) -> bool:
    """Parse the shape file fresh and validate a fixture data graph."""
    shapes = Graph().parse(SHAPES_FILE.as_posix(), format="turtle")
    data = Graph().parse(data=fixture_ttl, format="turtle")
    conforms, _, _ = validate(
        data_graph=data,
        shacl_graph=shapes,
        ont_graph=None,
        inference="none",
        advanced=True,
    )
    return conforms


def test_shape_file_exists_and_parses():
    assert SHAPES_FILE.is_file(), f"missing: {SHAPES_FILE}"
    shapes = Graph().parse(SHAPES_FILE.as_posix(), format="turtle")
    shape_node = URIRef(F5 + "SBBRealizationShape")
    assert (shape_node, RDF.type, URIRef(SH + "NodeShape")) in shapes
    # target is the SBB class, constraint on ea:satisfiesABB
    assert (shape_node, URIRef(SH + "targetClass"), URIRef(EA + "SolutionBuildingBlock")) in shapes
    assert (shape_node, URIRef(SH + "property"), None) in shapes


def test_dangling_sbb_violates():
    """Mutation: satisfiesABB pointing at a non-ABB node must be flagged."""
    fixture = """
    @prefix ea: <https://chatman.ai/ontology/enterprise-architecture#> .
    ea:badSbb a ea:SolutionBuildingBlock ;
      ea:satisfiesABB ea:notAnAbb .
    ea:notAnAbb a ea:SolutionBuildingBlock .   # wrong type: not an ABB
    """
    conforms = _validate_fixture(fixture)
    assert not conforms, "dangling SBB realization must violate the shape"


def test_missing_satisfies_abb_violates():
    """Mutation: an SBB with no ea:satisfiesABB at all must be flagged."""
    fixture = """
    @prefix ea: <https://chatman.ai/ontology/enterprise-architecture#> .
    ea:orphanSbb a ea:SolutionBuildingBlock .
    """
    conforms = _validate_fixture(fixture)
    assert not conforms, "SBB without ea:satisfiesABB must violate minCount 1"


def test_clean_sbb_conforms():
    """Clean fixture: one SBB whose satisfiesABB lands on a typed ABB conforms."""
    fixture = """
    @prefix ea: <https://chatman.ai/ontology/enterprise-architecture#> .
    ea:goodSbb a ea:SolutionBuildingBlock ;
      ea:satisfiesABB ea:abb1 .
    ea:abb1 a ea:ArchitectureBuildingBlock .
    """
    conforms = _validate_fixture(fixture)
    assert conforms, "clean SBB realization must conform to the shape"
