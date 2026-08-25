import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class DeterminismCourt(unittest.TestCase):
    def test_projection_queries_are_ordered_or_scalar(self):
        queries = sorted((ROOT / "queries").glob("*.rq"))
        self.assertEqual(25, len(queries))
        for query in queries:
            text = query.read_text()
            self.assertTrue("ORDER BY" in text or "COUNT(" in text, query.name)

if __name__ == "__main__": unittest.main()
