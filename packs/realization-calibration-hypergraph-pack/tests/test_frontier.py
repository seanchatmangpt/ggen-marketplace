from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FrontierCourt(unittest.TestCase):
    def test_distinct_search_variants_survive(self):
        queries = {p.name for p in (ROOT / "queries").glob("*.rq")}
        required = {
            "40-conservative-yield.rq",
            "50-optimistic-yield.rq",
            "60-reuse-adjusted-yield.rq",
            "70-failed-edge-topology.rq",
            "80-calibrated-frontier.rq",
        }
        self.assertTrue(required <= queries)

    def test_failed_edges_are_preserved_as_topology(self):
        query = (ROOT / "queries/70-failed-edge-topology.rq").read_text()
        self.assertIn("FILTER(?failures > 0)", query)
        self.assertIn("missingPrimitive", query)


if __name__ == "__main__":
    unittest.main()
