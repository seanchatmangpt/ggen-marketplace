import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Determinism(unittest.TestCase):
 def test_projection_ordering(self):
  for p in (ROOT/'queries').glob('*.rq'): self.assertIn('ORDER BY',p.read_text())
if __name__=='__main__': unittest.main()
