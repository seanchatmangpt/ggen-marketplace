import pathlib, subprocess, sys, unittest
ROOT=pathlib.Path(__file__).parents[1]
class AmbientDoTest(unittest.TestCase):
 def test_refuses_ambient_do(self):
  p=subprocess.run([sys.executable,ROOT/'gates/validate_rebloom.py',ROOT/'fixtures/ambient-do-plan.json'],capture_output=True,text=True)
  self.assertEqual(p.returncode,4); self.assertIn('REFUSED[AMBIENT_DO_AUTHORITY]',p.stdout)
if __name__=='__main__': unittest.main()
