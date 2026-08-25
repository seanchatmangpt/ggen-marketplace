import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class DeterminismTest(unittest.TestCase):
    def test_all_select_queries_order_results(self):
        for path in (ROOT / "queries").glob("*.rq"):
            self.assertIn("ORDER BY", path.read_text(), path.name)

if __name__ == "__main__": unittest.main()
