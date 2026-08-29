import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class PartialOrderCourt(unittest.TestCase):
 def test_ready_query_requires_compatibility_before_rank_order(self):
  q=(ROOT/'queries'/'10-consumer-ready-set.rq').read_text()
  self.assertIn('COMPATIBLE_READY', q)
  self.assertIn('FILTER NOT EXISTS', q)
  self.assertIn('ORDER BY ?rank', q)
if __name__=='__main__': unittest.main()
