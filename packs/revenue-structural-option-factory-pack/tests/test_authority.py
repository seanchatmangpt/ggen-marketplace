import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class AuthorityCourt(unittest.TestCase):
 def test_no_projection_claims_do(self):
  for p in ROOT.rglob('*'):
   if p.is_file() and p.suffix in {'.rq','.tera','.ttl'}:
    self.assertNotIn('authority":"DO"',p.read_text())
if __name__=='__main__': unittest.main()
