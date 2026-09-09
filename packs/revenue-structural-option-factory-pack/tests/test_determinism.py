import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class RevenueStructuralOptionDeterminism(unittest.TestCase):
    def test_queries_are_ordered(self):
        queries = list((ROOT / "queries").glob("*.rq"))
        self.assertGreaterEqual(len(queries), 3)
        for query in queries:
            self.assertIn("ORDER BY", query.read_text())

if __name__ == "__main__":
    unittest.main()
