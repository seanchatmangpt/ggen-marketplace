import pathlib, subprocess, sys, unittest

ROOT = pathlib.Path(__file__).parents[1]
class ValidPlanTest(unittest.TestCase):
    def test_valid_plan_is_alive(self):
        p = subprocess.run([sys.executable, ROOT/'gates/validate_rebloom.py', ROOT/'fixtures/valid-plan.json'], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout+p.stderr)
        self.assertIn('ALIVE', p.stdout)

if __name__ == '__main__': unittest.main()
