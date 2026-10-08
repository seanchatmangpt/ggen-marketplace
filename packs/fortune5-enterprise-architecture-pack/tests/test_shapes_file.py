# tests/test_shapes_file.py — prove that shapes/00-metamodel-hygiene.shacl.ttl
# is the same law as the inline copy in ontology.ttl (DoD #9 fence).
#
# Court: the extracted shape file must (a) parse as Turtle, (b) pyshacl-flag a
# conflation individual (a SolutionGroup also typed as an ea: class), and
# (c) accept a clean SolutionGroup. Anti-vacuity: (b) is the mutation.
#
# Real files, real pyshacl — no mocks (Chicago discipline).

from pathlib import Path

import pytest
from rdflib import Graph, RDF, RDFS, OWL, URIRef
from pyshacl import validate

PACK_DIR = Path(__file__).resolve().parents[1]
SHAPES_FILE = PACK_DIR / "shapes" / "00-metamodel-hygiene.shacl.ttl"
ONTOLOGY = PACK_DIR / "ontology.ttl"

F5 = "https://ggen.io/ontology/fortune5-enterprise-architecture#"
EA = "https://chatman.ai/ontology/enterprise-architecture#"
XSD_STRING = URIRef("http://www.w3.org/2001/XMLSchema#string")


def _graph_with_shapes(fixture_ttl: str) -> tuple[Graph, bool]:
    """Parse the shape file fresh and validate a fixture data graph."""
    shapes = Graph().parse(SHAPES_FILE.as_posix(), format="turtle")
    data = Graph().parse(data=fixture_ttl, format="turtle")
    # disjointness classes come from the ontology vocabulary
    data.parse(ONTOLOGY.as_posix(), format="turtle")
    conforms, _, _ = validate(
        data_graph=data,
        shacl_graph=shapes,
        ont_graph=None,
        inference="none",
        advanced=True,
    )
    return data, conforms


def test_shape_file_exists_and_parses():
    assert SHAPES_FILE.is_file(), f"missing: {SHAPES_FILE}"
    shapes = Graph().parse(SHAPES_FILE.as_posix(), format="turtle")
    shape_node = URIRef(F5 + "SolutionGroupShape")
    assert (shape_node, RDF.type, URIRef("http://www.w3.org/ns/shacl#NodeShape")) in shapes
    disjoint = list(shapes.subjects(RDF.type, OWL.AllDisjointClasses))
    assert disjoint, "AllDisjointClasses fence missing from extracted file"


def test_conflation_individual_violates():
    """Mutation: a SolutionGroup also typed as an SBB must be flagged."""
    fixture = """
    @prefix f5ea: <https://ggen.io/ontology/fortune5-enterprise-architecture#> .
    @prefix ea:   <https://chatman.ai/ontology/enterprise-architecture#> .
    f5ea:badGroup a f5ea:SolutionGroup, ea:SolutionBuildingBlock ;
      f5ea:groupKey "bad" ;
      f5ea:groupsSBB <https://example.com/sbb1> .
    """
    _, conforms = _graph_with_shapes(fixture)
    assert not conforms, "conflation individual must violate the extracted shape"


def test_clean_group_conforms():
    """Clean fixture: one SolutionGroup referencing a typed SBB conforms."""
    fixture = """
    @prefix f5ea: <https://ggen.io/ontology/fortune5-enterprise-architecture#> .
    @prefix ea:   <https://chatman.ai/ontology/enterprise-architecture#> .
    f5ea:goodGroup a f5ea:SolutionGroup ;
      f5ea:groupKey "good" ;
      f5ea:groupsSBB f5ea:sbb1 .
    f5ea:sbb1 a ea:SolutionBuildingBlock .
    """
    _, conforms = _graph_with_shapes(fixture)
    assert conforms, "clean SolutionGroup must conform to the extracted shape"
