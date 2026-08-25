import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class QueryOrderingCourt(unittest.TestCase):
    def test_projection_queries_are_ordered(self):
        for path in sorted((ROOT / "queries").glob("*.rq")):
            text = path.read_text(encoding="utf-8")
            if text.lstrip().startswith("PREFIX") and "SELECT" in text:
                self.assertIn("ORDER BY", text, path.name)

if __name__ == "__main__":
    unittest.main()
