import unittest
from pathlib import Path
ROOT = Path(__file__).parents[1]
class Replay(unittest.TestCase):
    def test_queries_are_stably_named(self):
        names = [p.name for p in sorted((ROOT/'queries').glob('*.rq'))]
        self.assertEqual(names, sorted(names))
        self.assertEqual(len({n.split('-',1)[0] for n in names}), len(names))
if __name__ == '__main__': unittest.main()
