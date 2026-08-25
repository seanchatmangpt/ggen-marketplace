import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class CounterfactualFrontierDeterminismTest(unittest.TestCase):
    def test_all_projection_queries_have_explicit_order(self):
        for name in ("90-pareto-frontier.rq", "91-replayable-frontier.rq"):
            query = (ROOT / "queries" / name).read_text(encoding="utf-8")
            self.assertIn("ORDER BY", query)


if __name__ == "__main__":
    unittest.main()
