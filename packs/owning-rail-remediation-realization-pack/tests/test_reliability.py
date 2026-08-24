import importlib.util
import pathlib
import unittest

PATH = pathlib.Path(__file__).parents[1] / "scripts" / "reliability.py"
SPEC = importlib.util.spec_from_file_location("reliability", PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

class ReliabilityCourt(unittest.TestCase):
    def test_wilson_and_rate(self):
        lower, upper = MOD.wilson(8, 10)
        self.assertLess(lower, 0.8)
        self.assertGreater(upper, 0.8)
        self.assertEqual(MOD.realized_rate(["REALIZED", "UNREALIZED"]), 0.5)
