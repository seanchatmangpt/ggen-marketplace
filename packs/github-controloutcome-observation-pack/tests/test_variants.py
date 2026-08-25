import unittest
from pathlib import Path
ROOT = Path(__file__).parents[1]
class Variants(unittest.TestCase):
    def test_variant_count(self): self.assertGreaterEqual(len(list((ROOT/'queries').glob('*.rq'))), 9)
    def test_distinct_confidence_variants(self):
        names = {p.name for p in (ROOT/'queries').glob('*.rq')}
        self.assertTrue(any('wilson' in n for n in names) and any('laplace' in n for n in names))
if __name__ == '__main__': unittest.main()
