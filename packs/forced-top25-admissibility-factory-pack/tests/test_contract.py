import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class ForcedTop25FactoryCourt(unittest.TestCase):
 def test_projection_is_non_actuating(self):
  text=(ROOT/'templates'/'consumer-subject.json.tera').read_text()
  self.assertIn('"consequential_do":false', text)
  self.assertIn('"authority":"VERIFY|CONSTRUCT"', text)
 def test_ready_set_legality_precedes_rank(self):
  q=(ROOT/'queries'/'10-ready-set.rq').read_text()
  self.assertIn('COMPATIBLE_READY', q)
  self.assertIn('FILTER NOT EXISTS', q)
  self.assertIn('ORDER BY ?rank', q)
 def test_gap_projection_preserves_unknown_targets(self):
  q=(ROOT/'queries'/'20-admissibility-gaps.rq').read_text()
  self.assertIn('FILTER NOT EXISTS', q)
if __name__=='__main__': unittest.main()
