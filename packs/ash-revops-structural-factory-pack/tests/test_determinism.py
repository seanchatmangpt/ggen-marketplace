from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class DeterminismCourt(unittest.TestCase):
    def test_projection_queries_have_explicit_order(self):
        for query in (ROOT / 'queries').glob('*.rq'):
            self.assertIn('ORDER BY', query.read_text(), query.name)

if __name__ == '__main__': unittest.main()
