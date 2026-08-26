import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class QueryOrderCourt(unittest.TestCase):
 def test_queries_are_ordered(self):
  for p in (ROOT/'queries').glob('*.rq'): self.assertIn('ORDER BY',p.read_text(),p.name)
if __name__=='__main__': unittest.main()
