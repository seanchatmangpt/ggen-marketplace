import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class CellBoundaryCourt(unittest.TestCase):
 def test_unknowns_are_returned_not_guessed(self):
  q=(ROOT/'queries'/'40-admissibility-return-set.rq').read_text(); t=(ROOT/'templates'/'admissibility-return.json.tera').read_text()
  self.assertIn('compatibilityState "UNKNOWN"', q)
  self.assertIn('"return_to":"CELL1"', t)
  self.assertIn('"authority":"SELECT"', t)
if __name__=='__main__': unittest.main()
