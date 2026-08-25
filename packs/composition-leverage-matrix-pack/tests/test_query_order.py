import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class QueryOrderCourt(unittest.TestCase):
    def test_select_queries_are_ordered(self):
        for path in (ROOT / "queries").glob("*.rq"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("ORDER BY", text, path.name)

if __name__ == "__main__": unittest.main()
