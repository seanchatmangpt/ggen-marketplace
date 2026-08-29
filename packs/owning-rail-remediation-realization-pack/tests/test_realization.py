import importlib.util
import pathlib
import unittest

PATH = pathlib.Path(__file__).parents[1] / "scripts" / "realization.py"
SPEC = importlib.util.spec_from_file_location("realization", PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

class RealizationCourt(unittest.TestCase):
    def test_relief_and_regression(self):
        self.assertEqual(MOD.Realization(3, 0, "PASS").classify(), "REALIZED")
        self.assertEqual(MOD.Realization(2, 3, "PASS").classify(), "REGRESSED")
        self.assertEqual(MOD.Realization(1, 1, "FAIL").classify(), "BUILD_BROKEN")
