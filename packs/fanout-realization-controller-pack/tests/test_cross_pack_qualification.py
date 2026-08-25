import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class CrossPackQualificationBoundaryTest(unittest.TestCase):
    def test_external_fanout_edges_are_explicitly_stubbed_for_isolated_qualification(self):
        consumer = (ROOT / "qualification/consumer.ttl").read_text(encoding="utf-8")
        for edge in ("edgeA", "edgeB", "edgeC", "edgeD", "edgeE"):
            self.assertIn(f"mfc:{edge} a mfc:FanoutEdge .", consumer)

    def test_owner_facts_are_not_duplicated_into_consumer_fixture(self):
        consumer = (ROOT / "qualification/consumer.ttl").read_text(encoding="utf-8")
        for predicate in ("mfc:asset", "mfc:consumer", "mfc:expectedQualifiedActions"):
            self.assertNotIn(predicate, consumer)


if __name__ == "__main__":
    unittest.main()
