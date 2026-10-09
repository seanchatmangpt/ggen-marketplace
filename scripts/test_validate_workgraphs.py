#!/usr/bin/env python3
"""Chicago-style tests for scripts/validate_workgraphs.py shape selection.

Real collaborator: the real pyshacl validator over the real shipped
ggen_igniter shapes (work-order.shacl.ttl and goal-checkpoint.shacl.ttl) and
real graph files written to a tmp dir; when the real castle precedent goal
graphs exist on disk they are validated as-is. Assertions are on the real
conformance reports. No mocks, no stubs.
"""
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import validate_workgraphs as vw  # noqa: E402

CASTLE_10_8 = Path.home() / "castle/docs/sjira/v26.10.8/goal.ttl"
CASTLE_9_28 = Path.home() / "castle/docs/sjira/v26.9.28/goal.ttl"

MINIMAL_GOAL = """\
@prefix sj: <https://ggen-igniter.dev/ontology/semantic-jira#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix ex: <https://example.org/goal#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:root
    a sj:GoalCheckpoint ;
    dcterms:identifier "EX-ROOT" ;
    rdfs:label "minimal goal graph" ;
    sj:repository "example/repo" ;
    sj:baseSha "%(sha)s" ;
    sj:authorityCeiling "CONSTRUCT" ;
    sj:replayIdentity "semantic-jira:example:EX-ROOT" ;
    sj:stopQuery "ASK { }" ;
    sj:falsifier "the goal never falsifies" .
"""

WORK_ORDER_GRAPH = """\
@prefix sj: <https://ggen-igniter.dev/ontology/semantic-jira#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix ex: <https://example.org/wo#> .

ex:order
    a sj:WorkOrder ;
    dcterms:identifier "EX-1" ;
    sj:repository "example/repo" ;
    sj:baseSha "%(sha)s" ;
    sj:subject "example subject" ;
    sj:standing "UNKNOWN" ;
    sj:authorityCeiling "CONSTRUCT" .
"""


def _fill(tpl: str) -> str:
    return tpl % {"sha": "a" * 40}


def _run_graph(source: str) -> dict:
    with tempfile.NamedTemporaryFile("w", suffix=".ttl", delete=False) as f:
        f.write(source)
        path = f.name
    try:
        g = vw.load_graph(Path(path))
        return vw.run_one("fixture", str(path))
    finally:
        Path(path).unlink(missing_ok=True)


class ShapeSelectionTest(unittest.TestCase):
    def test_goal_graph_selects_goal_checkpoint_shape(self):
        r = _run_graph(_fill(MINIMAL_GOAL))
        self.assertEqual(r["goal_checkpoints"], 1)
        self.assertEqual(r["work_orders"], 0)
        self.assertTrue(r["shapes"].endswith("goal-checkpoint.shacl.ttl"))
        self.assertTrue(r["conforms"], r["violations"])

    def test_work_order_graph_selects_work_order_shape(self):
        r = _run_graph(_fill(WORK_ORDER_GRAPH))
        self.assertEqual(r["work_orders"], 1)
        self.assertTrue(r["shapes"].endswith("work-order.shacl.ttl"))

    def test_corrupted_goal_graph_bad_sha_violates(self):
        bad = re.sub(
            r'sj:baseSha "[0-9a-f]{40}"', 'sj:baseSha "deadbeef"', _fill(MINIMAL_GOAL)
        )
        self.assertNotEqual(bad, _fill(MINIMAL_GOAL))
        r = _run_graph(bad)
        self.assertFalse(r["conforms"])
        messages = [m for _f, _p, _v, m in r["violations"]]
        self.assertTrue(any("pattern" in m for m in messages), messages)

    def test_corrupted_goal_graph_missing_replay_identity_violates(self):
        bad = re.sub(
            r"\n\s*sj:replayIdentity \"[^\"]*\" ;", "", _fill(MINIMAL_GOAL)
        )
        self.assertNotEqual(bad, _fill(MINIMAL_GOAL))
        r = _run_graph(bad)
        self.assertFalse(r["conforms"])
        messages = [m for _f, _p, _v, m in r["violations"]]
        self.assertTrue(
            any("replayIdentity" in m for m in messages), messages
        )


@unittest.skipUnless(
    CASTLE_10_8.exists() and CASTLE_9_28.exists(),
    "castle precedent graphs not present on this machine",
)
class CastlePrecedentTest(unittest.TestCase):
    def test_castle_v26_10_8_goal_graph_conforms(self):
        g = vw.load_graph(CASTLE_10_8)
        shapes = vw.load_graph(vw.GC_SHAPES)
        from pyshacl import validate

        conforms, _, text = validate(
            data_graph=g, shacl_graph=shapes, inference="none", advanced=True
        )
        self.assertTrue(conforms, text)

    def test_castle_v26_9_28_goal_graph_conforms(self):
        g = vw.load_graph(CASTLE_9_28)
        shapes = vw.load_graph(vw.GC_SHAPES)
        from pyshacl import validate

        conforms, _, text = validate(
            data_graph=g, shacl_graph=shapes, inference="none", advanced=True
        )
        self.assertTrue(conforms, text)

    def test_full_run_reports_castle_conforming_under_goal_shape(self):
        targets = [t for t in vw.TARGETS if t[0] == "castle"]
        r = vw.run_one(*targets[0])
        self.assertTrue(r["shapes"].endswith("goal-checkpoint.shacl.ttl"))
        self.assertTrue(r["conforms"], r["violations"])
        self.assertGreaterEqual(r["goal_checkpoints"], 1)


if __name__ == "__main__":
    unittest.main()
