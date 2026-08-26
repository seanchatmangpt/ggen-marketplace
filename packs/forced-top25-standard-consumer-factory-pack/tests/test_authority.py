import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class AuthorityCourt(unittest.TestCase):
 def test_generated_plans_never_claim_do(self):
  for p in (ROOT/'templates').glob('*.tera'):
   text=p.read_text(); self.assertIn('"consequential_do":false', text); self.assertNotIn('"authority":"DO"', text)
if __name__=='__main__': unittest.main()
