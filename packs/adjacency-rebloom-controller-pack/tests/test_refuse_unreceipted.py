import pathlib, subprocess, sys, unittest
ROOT=pathlib.Path(__file__).parents[1]
class ReceiptTest(unittest.TestCase):
 def test_refuses_unreceipted_wave(self):
  p=subprocess.run([sys.executable,ROOT/'gates/validate_rebloom.py',ROOT/'fixtures/unreceipted-plan.json'],capture_output=True,text=True)
  self.assertEqual(p.returncode,5); self.assertIn('REFUSED[UNRECEIPTED_REBLOOM]',p.stdout)
if __name__=='__main__': unittest.main()
