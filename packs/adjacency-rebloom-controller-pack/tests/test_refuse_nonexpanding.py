import pathlib, subprocess, sys, unittest
ROOT=pathlib.Path(__file__).parents[1]
class BoundsTest(unittest.TestCase):
 def test_refuses_nonexpanding_bounds(self):
  p=subprocess.run([sys.executable,ROOT/'gates/validate_rebloom.py',ROOT/'fixtures/unbounded-plan.json'],capture_output=True,text=True)
  self.assertEqual(p.returncode,6); self.assertIn('REFUSED[NON_EXPANDING_BOUND]',p.stdout)
if __name__=='__main__': unittest.main()
